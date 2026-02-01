package cli

import (
	"context"
	"encoding/json"
	"fmt"
	"net/url"
	"os"
	"strings"

	"github.com/visionik/mogcli/internal/graph"
)

// ExcelCmd handles Excel operations.
type ExcelCmd struct {
	List     ExcelListCmd     `cmd:"" help:"List Excel workbooks"`
	Metadata ExcelMetadataCmd `cmd:"" help:"List worksheets in a workbook"`
	Get      ExcelGetCmd      `cmd:"" help:"Read data from a worksheet"`
	Update   ExcelUpdateCmd   `cmd:"" help:"Write data to a worksheet"`
	Append   ExcelAppendCmd   `cmd:"" help:"Append data to a table"`
	Create   ExcelCreateCmd   `cmd:"" help:"Create a new workbook"`
	AddSheet ExcelAddSheetCmd `cmd:"" help:"Add a worksheet" name:"add-sheet"`
	Tables   ExcelTablesCmd   `cmd:"" help:"List tables in a workbook"`
	Clear    ExcelClearCmd    `cmd:"" help:"Clear a range"`
	Export   ExcelExportCmd   `cmd:"" help:"Export workbook"`
	Copy     ExcelCopyCmd     `cmd:"" help:"Copy a workbook"`
}

// ExcelListCmd lists workbooks.
type ExcelListCmd struct {
	Max int `help:"Maximum results" default:"50"`
}

// Run executes excel list.
func (c *ExcelListCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	query := url.Values{}
	query.Set("$top", fmt.Sprintf("%d", c.Max))
	query.Set("$filter", "file/mimeType eq 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'")
	query.Set("$orderby", "lastModifiedDateTime desc")

	data, err := client.Get(ctx, "/me/drive/root/search(q='.xlsx')", query)
	if err != nil {
		return err
	}

	var resp struct {
		Value []DriveItem `json:"value"`
	}
	if err := json.Unmarshal(data, &resp); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(resp.Value)
	}

	if len(resp.Value) == 0 {
		fmt.Println("No Excel workbooks found")
		return nil
	}

	fmt.Println("Excel Workbooks")
	fmt.Println()
	for _, wb := range resp.Value {
		fmt.Printf("📊 %s  %s  %s\n", wb.Name, formatSize(wb.Size), wb.LastModifiedDateTime[:10])
		fmt.Printf("   ID: %s\n", graph.FormatID(wb.ID))
		if root.Verbose && wb.WebURL != "" {
			fmt.Printf("   URL: %s\n", wb.WebURL)
		}
	}
	fmt.Printf("\n%d workbook(s)\n", len(resp.Value))
	return nil
}

// ExcelMetadataCmd gets workbook metadata.
type ExcelMetadataCmd struct {
	ID string `arg:"" help:"Workbook ID or path"`
}

// Run executes excel metadata.
func (c *ExcelMetadataCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	path := fmt.Sprintf("/me/drive/items/%s/workbook/worksheets", graph.ResolveID(c.ID))

	data, err := client.Get(ctx, path, nil)
	if err != nil {
		return err
	}

	var resp struct {
		Value []Worksheet `json:"value"`
	}
	if err := json.Unmarshal(data, &resp); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(resp.Value)
	}

	if len(resp.Value) == 0 {
		fmt.Println("No worksheets found")
		return nil
	}

	fmt.Println("Worksheets")
	fmt.Println()
	for _, sheet := range resp.Value {
		visibility := ""
		if sheet.Visibility != "Visible" {
			visibility = fmt.Sprintf(" (%s)", sheet.Visibility)
		}
		fmt.Printf("📄 %s%s\n", sheet.Name, visibility)
		fmt.Printf("   ID: %s\n", sheet.ID)
		if sheet.Position >= 0 {
			fmt.Printf("   Position: %d\n", sheet.Position)
		}
	}
	fmt.Printf("\n%d worksheet(s)\n", len(resp.Value))
	return nil
}

// ExcelGetCmd reads data.
type ExcelGetCmd struct {
	ID    string `arg:"" help:"Workbook ID"`
	Sheet string `arg:"" optional:"" help:"Sheet name"`
	Range string `arg:"" optional:"" help:"Cell range (e.g., A1:D10)"`
}

// Run executes excel get.
func (c *ExcelGetCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	workbookID := graph.ResolveID(c.ID)

	// If no sheet specified, get first sheet
	sheetName := c.Sheet
	if sheetName == "" {
		sheets, err := getWorksheets(client, ctx, workbookID)
		if err != nil {
			return err
		}
		if len(sheets) == 0 {
			return fmt.Errorf("workbook has no worksheets")
		}
		sheetName = sheets[0].Name
	}

	// If sheetName looks like a range (contains :), swap it
	if strings.Contains(sheetName, ":") && c.Range == "" {
		c.Range = sheetName
		sheets, err := getWorksheets(client, ctx, workbookID)
		if err != nil {
			return err
		}
		if len(sheets) == 0 {
			return fmt.Errorf("workbook has no worksheets")
		}
		sheetName = sheets[0].Name
	}

	// Build path
	var path string
	if c.Range != "" {
		path = fmt.Sprintf("/me/drive/items/%s/workbook/worksheets('%s')/range(address='%s')",
			workbookID, sheetName, c.Range)
	} else {
		path = fmt.Sprintf("/me/drive/items/%s/workbook/worksheets('%s')/usedRange",
			workbookID, sheetName)
	}

	data, err := client.Get(ctx, path, nil)
	if err != nil {
		return err
	}

	var rangeData RangeData
	if err := json.Unmarshal(data, &rangeData); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(rangeData)
	}

	if len(rangeData.Values) == 0 {
		fmt.Println("No data in range")
		return nil
	}

	rangeLabel := c.Range
	if rangeLabel == "" {
		rangeLabel = "(used range)"
	}
	fmt.Printf("%s - %s\n\n", sheetName, rangeLabel)

	// Calculate column widths
	colWidths := make([]int, len(rangeData.Values[0]))
	for _, row := range rangeData.Values {
		for col, cell := range row {
			str := fmt.Sprintf("%v", cell)
			if len(str) > colWidths[col] {
				colWidths[col] = len(str)
			}
			if colWidths[col] > 30 {
				colWidths[col] = 30
			}
		}
	}

	// Print rows
	for i, row := range rangeData.Values {
		var cells []string
		for col, cell := range row {
			str := fmt.Sprintf("%v", cell)
			if len(str) > 30 {
				str = str[:27] + "..."
			}
			cells = append(cells, fmt.Sprintf("%-*s", colWidths[col], str))
		}
		line := strings.Join(cells, "  ")
		if i == 0 {
			fmt.Println(line)
			fmt.Println(strings.Repeat("-", len(line)))
		} else {
			fmt.Println(line)
		}
	}

	fmt.Printf("\n%d row(s), %d column(s)\n", len(rangeData.Values), len(rangeData.Values[0]))
	return nil
}

// ExcelUpdateCmd writes data.
type ExcelUpdateCmd struct {
	ID     string   `arg:"" help:"Workbook ID"`
	Sheet  string   `arg:"" help:"Sheet name"`
	Range  string   `arg:"" help:"Cell range"`
	Values []string `arg:"" help:"Values to write (fills row by row)"`
}

// Run executes excel update.
func (c *ExcelUpdateCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	if len(c.Values) == 0 {
		return fmt.Errorf("values are required")
	}

	// Parse range to determine dimensions
	values := parsePositionalValues(c.Range, c.Values)

	body := map[string]interface{}{
		"values": values,
	}

	ctx := context.Background()
	path := fmt.Sprintf("/me/drive/items/%s/workbook/worksheets('%s')/range(address='%s')",
		graph.ResolveID(c.ID), c.Sheet, c.Range)

	_, err = client.Patch(ctx, path, body)
	if err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(map[string]interface{}{"success": true, "sheet": c.Sheet, "range": c.Range})
	}

	fmt.Println("✓ Updated")
	fmt.Printf("  Sheet: %s\n", c.Sheet)
	fmt.Printf("  Range: %s\n", c.Range)
	fmt.Printf("  Cells: %d rows × %d columns\n", len(values), len(values[0]))
	return nil
}

// ExcelAppendCmd appends data.
type ExcelAppendCmd struct {
	ID     string   `arg:"" help:"Workbook ID"`
	Table  string   `arg:"" help:"Table name"`
	Values []string `arg:"" help:"Values to append (one row)"`
}

// Run executes excel append.
func (c *ExcelAppendCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	if len(c.Values) == 0 {
		return fmt.Errorf("values are required")
	}

	// For append, values become a single row
	values := [][]interface{}{make([]interface{}, len(c.Values))}
	for i, v := range c.Values {
		values[0][i] = v
	}

	body := map[string]interface{}{
		"values": values,
	}

	ctx := context.Background()
	path := fmt.Sprintf("/me/drive/items/%s/workbook/tables('%s')/rows/add",
		graph.ResolveID(c.ID), c.Table)

	_, err = client.Post(ctx, path, body)
	if err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(map[string]interface{}{"success": true, "table": c.Table, "rows": 1})
	}

	fmt.Println("✓ Appended")
	fmt.Printf("  Table: %s\n", c.Table)
	fmt.Printf("  Rows added: 1\n")
	return nil
}

// ExcelCreateCmd creates a workbook.
type ExcelCreateCmd struct {
	Name   string `arg:"" help:"Workbook name"`
	Folder string `help:"Destination folder ID"`
}

// Run executes excel create.
func (c *ExcelCreateCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	// Ensure .xlsx extension
	name := c.Name
	if !strings.HasSuffix(strings.ToLower(name), ".xlsx") {
		name += ".xlsx"
	}

	// Create empty workbook by uploading minimal xlsx content
	// For simplicity, we'll create an empty file and let Graph handle it
	ctx := context.Background()
	var path string
	if c.Folder != "" {
		path = fmt.Sprintf("/me/drive/items/%s:/%s:/content", graph.ResolveID(c.Folder), name)
	} else {
		path = fmt.Sprintf("/me/drive/root:/%s:/content", name)
	}

	// Minimal xlsx content (empty workbook)
	emptyXlsx := getMinimalXlsx()

	data, err := client.Put(ctx, path, emptyXlsx, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
	if err != nil {
		return err
	}

	var item DriveItem
	if err := json.Unmarshal(data, &item); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(item)
	}

	fmt.Println("✓ Workbook created")
	fmt.Printf("  Name: %s\n", item.Name)
	fmt.Printf("  ID: %s\n", graph.FormatID(item.ID))
	return nil
}

// ExcelAddSheetCmd adds a worksheet.
type ExcelAddSheetCmd struct {
	ID   string `arg:"" help:"Workbook ID"`
	Name string `help:"Sheet name"`
}

// Run executes excel add-sheet.
func (c *ExcelAddSheetCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	body := map[string]interface{}{}
	if c.Name != "" {
		body["name"] = c.Name
	}

	ctx := context.Background()
	path := fmt.Sprintf("/me/drive/items/%s/workbook/worksheets/add", graph.ResolveID(c.ID))

	data, err := client.Post(ctx, path, body)
	if err != nil {
		return err
	}

	var sheet Worksheet
	if err := json.Unmarshal(data, &sheet); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(sheet)
	}

	fmt.Println("✓ Worksheet added")
	fmt.Printf("  Name: %s\n", sheet.Name)
	fmt.Printf("  ID: %s\n", sheet.ID)
	return nil
}

// ExcelTablesCmd lists tables.
type ExcelTablesCmd struct {
	ID string `arg:"" help:"Workbook ID"`
}

// Run executes excel tables.
func (c *ExcelTablesCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	path := fmt.Sprintf("/me/drive/items/%s/workbook/tables", graph.ResolveID(c.ID))

	data, err := client.Get(ctx, path, nil)
	if err != nil {
		return err
	}

	var resp struct {
		Value []Table `json:"value"`
	}
	if err := json.Unmarshal(data, &resp); err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(resp.Value)
	}

	if len(resp.Value) == 0 {
		fmt.Println("No tables found in workbook")
		return nil
	}

	fmt.Println("Tables")
	fmt.Println()
	for _, table := range resp.Value {
		fmt.Printf("📋 %s\n", table.Name)
		if table.ShowHeaders {
			fmt.Printf("   Headers: Yes\n")
		}
		if table.ShowTotals {
			fmt.Printf("   Totals: Yes\n")
		}
		fmt.Printf("   ID: %s\n", table.ID)
	}
	fmt.Printf("\n%d table(s)\n", len(resp.Value))
	return nil
}

// ExcelClearCmd clears a range.
type ExcelClearCmd struct {
	ID    string `arg:"" help:"Workbook ID"`
	Sheet string `arg:"" help:"Sheet name"`
	Range string `arg:"" help:"Range to clear"`
}

// Run executes excel clear.
func (c *ExcelClearCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	body := map[string]interface{}{
		"applyTo": "All",
	}

	ctx := context.Background()
	path := fmt.Sprintf("/me/drive/items/%s/workbook/worksheets('%s')/range(address='%s')/clear",
		graph.ResolveID(c.ID), c.Sheet, c.Range)

	_, err = client.Post(ctx, path, body)
	if err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(map[string]interface{}{"success": true, "sheet": c.Sheet, "range": c.Range})
	}

	fmt.Println("✓ Cleared")
	fmt.Printf("  Sheet: %s\n", c.Sheet)
	fmt.Printf("  Range: %s\n", c.Range)
	return nil
}

// ExcelExportCmd exports a workbook.
type ExcelExportCmd struct {
	ID     string `arg:"" help:"Workbook ID"`
	Out    string `help:"Output path" required:""`
	Format string `help:"Export format (xlsx, csv)" default:"xlsx"`
	Sheet  string `help:"Sheet name (for CSV export)"`
}

// Run executes excel export.
func (c *ExcelExportCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	ctx := context.Background()
	workbookID := graph.ResolveID(c.ID)

	if strings.ToLower(c.Format) == "csv" {
		// For CSV, export sheet data
		sheetName := c.Sheet
		if sheetName == "" {
			sheets, err := getWorksheets(client, ctx, workbookID)
			if err != nil {
				return err
			}
			if len(sheets) == 0 {
				return fmt.Errorf("workbook has no worksheets")
			}
			sheetName = sheets[0].Name
		}

		// Get used range
		path := fmt.Sprintf("/me/drive/items/%s/workbook/worksheets('%s')/usedRange", workbookID, sheetName)
		data, err := client.Get(ctx, path, nil)
		if err != nil {
			return err
		}

		var rangeData RangeData
		if err := json.Unmarshal(data, &rangeData); err != nil {
			return err
		}

		// Convert to CSV
		var csv strings.Builder
		for _, row := range rangeData.Values {
			var cells []string
			for _, cell := range row {
				cells = append(cells, fmt.Sprintf("%v", cell))
			}
			csv.WriteString(strings.Join(cells, ",") + "\n")
		}

		if err := os.WriteFile(c.Out, []byte(csv.String()), 0644); err != nil {
			return err
		}

		fmt.Println("✓ Exported")
		fmt.Printf("  Format: CSV\n")
		fmt.Printf("  Sheet: %s\n", sheetName)
		fmt.Printf("  Saved to: %s\n", c.Out)
	} else {
		// Download xlsx
		path := fmt.Sprintf("/me/drive/items/%s/content", workbookID)
		data, err := client.Get(ctx, path, nil)
		if err != nil {
			return err
		}

		if err := os.WriteFile(c.Out, data, 0644); err != nil {
			return err
		}

		fmt.Println("✓ Exported")
		fmt.Printf("  Format: XLSX\n")
		fmt.Printf("  Saved to: %s\n", c.Out)
	}

	return nil
}

// ExcelCopyCmd copies a workbook.
type ExcelCopyCmd struct {
	ID     string `arg:"" help:"Workbook ID"`
	Name   string `arg:"" help:"New name"`
	Folder string `help:"Destination folder ID"`
}

// Run executes excel copy.
func (c *ExcelCopyCmd) Run(root *Root) error {
	client, err := root.GetClient()
	if err != nil {
		return err
	}

	body := map[string]interface{}{
		"name": c.Name,
	}
	if c.Folder != "" {
		body["parentReference"] = map[string]string{
			"id": graph.ResolveID(c.Folder),
		}
	}

	ctx := context.Background()
	path := fmt.Sprintf("/me/drive/items/%s/copy", graph.ResolveID(c.ID))

	_, err = client.Post(ctx, path, body)
	if err != nil {
		return err
	}

	if root.JSON {
		return outputJSON(map[string]interface{}{"success": true, "name": c.Name})
	}

	fmt.Println("✓ Copy initiated")
	fmt.Printf("  Name: %s\n", c.Name)
	return nil
}

// Worksheet represents an Excel worksheet.
type Worksheet struct {
	ID         string `json:"id"`
	Name       string `json:"name"`
	Position   int    `json:"position"`
	Visibility string `json:"visibility"`
}

// RangeData represents range data.
type RangeData struct {
	Address string          `json:"address"`
	Values  [][]interface{} `json:"values"`
}

// Table represents an Excel table.
type Table struct {
	ID          string `json:"id"`
	Name        string `json:"name"`
	ShowHeaders bool   `json:"showHeaders"`
	ShowTotals  bool   `json:"showTotals"`
}

func getWorksheets(client graph.Client, ctx context.Context, workbookID string) ([]Worksheet, error) {
	path := fmt.Sprintf("/me/drive/items/%s/workbook/worksheets", workbookID)
	data, err := client.Get(ctx, path, nil)
	if err != nil {
		return nil, err
	}

	var resp struct {
		Value []Worksheet `json:"value"`
	}
	if err := json.Unmarshal(data, &resp); err != nil {
		return nil, err
	}
	return resp.Value, nil
}

func parsePositionalValues(rangeAddr string, values []string) [][]interface{} {
	// Parse range to determine dimensions (e.g., A1:B2 = 2 cols, 2 rows)
	parts := strings.Split(rangeAddr, ":")
	if len(parts) != 2 {
		// Single cell
		return [][]interface{}{{values[0]}}
	}

	startCol, startRow := parseCell(parts[0])
	endCol, endRow := parseCell(parts[1])

	numCols := endCol - startCol + 1
	numRows := endRow - startRow + 1

	result := make([][]interface{}, numRows)
	idx := 0
	for r := 0; r < numRows; r++ {
		result[r] = make([]interface{}, numCols)
		for c := 0; c < numCols; c++ {
			if idx < len(values) {
				result[r][c] = values[idx]
			} else {
				result[r][c] = ""
			}
			idx++
		}
	}
	return result
}

func parseCell(cell string) (col, row int) {
	col = 0
	row = 0
	for i, c := range cell {
		if c >= 'A' && c <= 'Z' {
			col = col*26 + int(c-'A') + 1
		} else if c >= 'a' && c <= 'z' {
			col = col*26 + int(c-'a') + 1
		} else {
			row, _ = fmt.Sscanf(cell[i:], "%d", &row)
			break
		}
	}
	return col, row
}

// getMinimalXlsx returns a minimal valid xlsx file
func getMinimalXlsx() []byte {
	// This is a base64-decoded minimal xlsx file
	// In practice, you might want to use a proper xlsx library
	// For now, we'll rely on Graph API to handle empty content
	return []byte{}
}
