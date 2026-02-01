\
// assets/power-query-folder-ingest-template.pq
// Paste into Power Query Advanced Editor and adapt column names.
// Pattern: Folder -> Combine -> Promote headers -> Type -> Defensive column handling

let
    Source = Folder.Files("C:\\PATH_TO_SOURCE_FOLDER"),
    VisibleFiles = Table.SelectRows(Source, each [Attributes]?[Hidden]? <> true),
    AddedCustom = Table.AddColumn(VisibleFiles, "Transform File", each #"Transform File"([Content])),
    Expanded = Table.ExpandTableColumn(AddedCustom, "Transform File", Table.ColumnNames(#"Transform File"(VisibleFiles{0}[Content]))),
    Promoted = Table.PromoteHeaders(Expanded, [PromoteAllScalars=true]),
    // Defensive: ensure missing columns don't break refresh
    RequiredCols = {"PayNumber","Name","ISOWeek","Date"},
    WithAllCols = List.Accumulate(RequiredCols, Promoted, (state, col) => if List.Contains(Table.ColumnNames(state), col) then state else Table.AddColumn(state, col, each null)),
    Typed = Table.TransformColumnTypes(WithAllCols, {{"PayNumber", type text}, {"Name", type text}, {"ISOWeek", Int64.Type}, {"Date", type date}})
in
    Typed
