package cli

import (
	"context"
	"fmt"
	"os"
	"path"

	"github.com/visionik/sogcli/internal/config"
	"github.com/visionik/sogcli/internal/webdav"
)

// DriveCmd handles file operations.
type DriveCmd struct {
	Ls       DriveListCmd     `cmd:"" aliases:"list" help:"List files and folders"`
	Get      DriveGetCmd      `cmd:"" aliases:"stat,info" help:"Get file/folder metadata"`
	Download DriveDownloadCmd `cmd:"" help:"Download a file"`
	Upload   DriveUploadCmd   `cmd:"" aliases:"put" help:"Upload a file"`
	Mkdir    DriveMkdirCmd    `cmd:"" help:"Create a directory"`
	Delete   DriveDeleteCmd   `cmd:"" aliases:"rm,del" help:"Delete a file or directory"`
	Move     DriveMoveCmd     `cmd:"" aliases:"mv,rename" help:"Move or rename a file"`
	Copy     DriveCopyCmd     `cmd:"" aliases:"cp" help:"Copy a file"`
	Cat      DriveCatCmd      `cmd:"" help:"Output file contents to stdout"`
}

// DriveListCmd lists files.
type DriveListCmd struct {
	Path string `arg:"" optional:"" default:"/" help:"Remote path to list"`
	Long bool   `help:"Long format with details" short:"l"`
	All  bool   `help:"Show hidden files"`
}

// Run executes the drive ls command.
func (c *DriveListCmd) Run(root *Root) error {
	client, err := getWebDAVClient(root)
	if err != nil {
		return err
	}
	defer client.Close()

	ctx := context.Background()
	files, err := client.List(ctx, c.Path)
	if err != nil {
		return fmt.Errorf("failed to list: %w", err)
	}

	if len(files) == 0 {
		fmt.Println("Empty directory.")
		return nil
	}

	// Filter hidden files
	if !c.All {
		var visible []webdav.FileInfo
		for _, f := range files {
			if !webdav.IsHidden(f.Name) {
				visible = append(visible, f)
			}
		}
		files = visible
	}

	if root.JSON {
		return outputFilesJSON(files)
	}

	if c.Long {
		return outputFilesLong(files)
	}

	return outputFilesShort(files)
}

// DriveGetCmd gets file metadata (like gog drive get).
type DriveGetCmd struct {
	Path string `arg:"" help:"Path to inspect"`
}

// Run executes the drive get command.
func (c *DriveGetCmd) Run(root *Root) error {
	client, err := getWebDAVClient(root)
	if err != nil {
		return err
	}
	defer client.Close()

	ctx := context.Background()
	info, err := client.Stat(ctx, c.Path)
	if err != nil {
		return fmt.Errorf("failed to get info: %w", err)
	}

	if root.JSON {
		return outputFilesJSON([]webdav.FileInfo{*info})
	}

	fmt.Printf("Path:     %s\n", info.Path)
	fmt.Printf("Name:     %s\n", info.Name)
	fmt.Printf("Type:     %s\n", fileType(info))
	if !info.IsDir {
		fmt.Printf("Size:     %s (%d bytes)\n", webdav.FormatSize(info.Size), info.Size)
	}
	if info.ContentType != "" {
		fmt.Printf("MIME:     %s\n", info.ContentType)
	}
	if !info.Modified.IsZero() {
		fmt.Printf("Modified: %s\n", info.Modified.Format("2006-01-02 15:04:05"))
	}
	if info.ETag != "" {
		fmt.Printf("ETag:     %s\n", info.ETag)
	}
	return nil
}

// DriveDownloadCmd downloads a file.
type DriveDownloadCmd struct {
	Remote string `arg:"" help:"Remote file path"`
	Local  string `arg:"" optional:"" help:"Local path (default: current dir with same name)"`
}

// Run executes the drive download command.
func (c *DriveDownloadCmd) Run(root *Root) error {
	client, err := getWebDAVClient(root)
	if err != nil {
		return err
	}
	defer client.Close()

	local := c.Local
	if local == "" {
		local = path.Base(c.Remote)
	}

	ctx := context.Background()
	if err := client.Download(ctx, c.Remote, local); err != nil {
		return fmt.Errorf("failed to download: %w", err)
	}

	fmt.Printf("Downloaded: %s -> %s\n", c.Remote, local)
	return nil
}

// DriveUploadCmd uploads a file.
type DriveUploadCmd struct {
	Local  string `arg:"" help:"Local file path"`
	Remote string `arg:"" optional:"" help:"Remote path (default: / with same name)"`
}

// Run executes the drive upload command.
func (c *DriveUploadCmd) Run(root *Root) error {
	client, err := getWebDAVClient(root)
	if err != nil {
		return err
	}
	defer client.Close()

	remote := c.Remote
	if remote == "" {
		remote = "/" + path.Base(c.Local)
	}

	ctx := context.Background()
	if err := client.Upload(ctx, c.Local, remote); err != nil {
		return fmt.Errorf("failed to upload: %w", err)
	}

	fmt.Printf("Uploaded: %s -> %s\n", c.Local, remote)
	return nil
}

// DriveMkdirCmd creates a directory.
type DriveMkdirCmd struct {
	Path string `arg:"" help:"Directory path to create"`
}

// Run executes the drive mkdir command.
func (c *DriveMkdirCmd) Run(root *Root) error {
	client, err := getWebDAVClient(root)
	if err != nil {
		return err
	}
	defer client.Close()

	ctx := context.Background()
	if err := client.Mkdir(ctx, c.Path); err != nil {
		return fmt.Errorf("failed to create directory: %w", err)
	}

	fmt.Printf("Created: %s\n", c.Path)
	return nil
}

// DriveDeleteCmd deletes a file or directory.
type DriveDeleteCmd struct {
	Path string `arg:"" help:"Path to delete"`
}

// Run executes the drive delete command.
func (c *DriveDeleteCmd) Run(root *Root) error {
	client, err := getWebDAVClient(root)
	if err != nil {
		return err
	}
	defer client.Close()

	ctx := context.Background()
	if err := client.Delete(ctx, c.Path); err != nil {
		return fmt.Errorf("failed to delete: %w", err)
	}

	fmt.Printf("Deleted: %s\n", c.Path)
	return nil
}

// DriveMoveCmd moves/renames a file.
type DriveMoveCmd struct {
	Src string `arg:"" help:"Source path"`
	Dst string `arg:"" help:"Destination path"`
}

// Run executes the drive move command.
func (c *DriveMoveCmd) Run(root *Root) error {
	client, err := getWebDAVClient(root)
	if err != nil {
		return err
	}
	defer client.Close()

	ctx := context.Background()
	if err := client.Move(ctx, c.Src, c.Dst); err != nil {
		return fmt.Errorf("failed to move: %w", err)
	}

	fmt.Printf("Moved: %s -> %s\n", c.Src, c.Dst)
	return nil
}

// DriveCopyCmd copies a file.
type DriveCopyCmd struct {
	Src string `arg:"" help:"Source path"`
	Dst string `arg:"" help:"Destination path"`
}

// Run executes the drive copy command.
func (c *DriveCopyCmd) Run(root *Root) error {
	client, err := getWebDAVClient(root)
	if err != nil {
		return err
	}
	defer client.Close()

	ctx := context.Background()
	if err := client.Copy(ctx, c.Src, c.Dst); err != nil {
		return fmt.Errorf("failed to copy: %w", err)
	}

	fmt.Printf("Copied: %s -> %s\n", c.Src, c.Dst)
	return nil
}

// DriveCatCmd outputs file contents.
type DriveCatCmd struct {
	Path string `arg:"" help:"File path"`
}

// Run executes the drive cat command.
func (c *DriveCatCmd) Run(root *Root) error {
	client, err := getWebDAVClient(root)
	if err != nil {
		return err
	}
	defer client.Close()

	ctx := context.Background()
	if err := client.DownloadToWriter(ctx, c.Path, os.Stdout); err != nil {
		return fmt.Errorf("failed to read file: %w", err)
	}

	return nil
}

// getWebDAVClient creates a WebDAV client from config.
func getWebDAVClient(root *Root) (*webdav.Client, error) {
	cfg, err := config.Load()
	if err != nil {
		return nil, fmt.Errorf("failed to load config: %w", err)
	}

	email := root.Account
	if email == "" {
		email = cfg.DefaultAccount
	}
	if email == "" {
		return nil, fmt.Errorf("no account specified. Use --account or set a default")
	}

	acct, err := cfg.GetAccount(email)
	if err != nil {
		return nil, err
	}

	if acct.WebDAV.URL == "" {
		return nil, fmt.Errorf("no WebDAV URL configured for %s. Run: sog auth add %s --webdav-url <url>", email, email)
	}

	password, err := cfg.GetPasswordForProtocol(email, config.ProtocolWebDAV)
	if err != nil {
		return nil, fmt.Errorf("failed to get password: %w", err)
	}

	client, err := webdav.Connect(webdav.Config{
		URL:      acct.WebDAV.URL,
		Email:    email,
		Password: password,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to connect to WebDAV: %w", err)
	}

	return client, nil
}

// fileType returns a string describing the file type.
func fileType(info *webdav.FileInfo) string {
	if info.IsDir {
		return "directory"
	}
	return "file"
}

// outputFilesJSON outputs files as JSON.
func outputFilesJSON(files []webdav.FileInfo) error {
	for _, f := range files {
		ftype := "file"
		if f.IsDir {
			ftype = "dir"
		}
		fmt.Printf(`{"path":"%s","name":"%s","type":"%s","size":%d,"modified":"%s"}`+"\n",
			f.Path, f.Name, ftype, f.Size, f.Modified.Format("2006-01-02T15:04:05Z"))
	}
	return nil
}

// outputFilesShort outputs files in short format.
func outputFilesShort(files []webdav.FileInfo) error {
	for _, f := range files {
		name := f.Name
		if f.IsDir {
			name += "/"
		}
		fmt.Println(name)
	}
	return nil
}

// outputFilesLong outputs files in long format.
func outputFilesLong(files []webdav.FileInfo) error {
	for _, f := range files {
		ftype := "-"
		if f.IsDir {
			ftype = "d"
		}
		size := webdav.FormatSize(f.Size)
		if f.IsDir {
			size = "-"
		}
		modified := "-"
		if !f.Modified.IsZero() {
			modified = f.Modified.Format("2006-01-02 15:04")
		}
		name := f.Name
		if f.IsDir {
			name += "/"
		}
		fmt.Printf("%s %8s %16s %s\n", ftype, size, modified, name)
	}
	return nil
}
