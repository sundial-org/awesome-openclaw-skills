# MediaSets Commands

Manage media sets and media content with transaction-based operations.

## RID Formats
- Media Sets: `ri.mediasets.main.media-set.{uuid}`
- Media Items: `ri.mediasets.main.media-item.{uuid}`

## Get Media Item Info

```bash
pltr media-sets get MEDIA_SET_RID MEDIA_ITEM_RID [--preview] [--format FORMAT]

# Example
pltr media-sets get ri.mediasets.main.media-set.abc123 ri.mediasets.main.media-item.def456
```

## Get Media Item by Path

```bash
pltr media-sets get-by-path MEDIA_SET_RID MEDIA_ITEM_PATH [--branch BRANCH] [--preview]

# Example
pltr media-sets get-by-path ri.mediasets.main.media-set.abc123 "/images/photo.jpg"
```

## Get Media Reference

Get embedding reference for a media item:

```bash
pltr media-sets reference MEDIA_SET_RID MEDIA_ITEM_RID [--preview]

# Example
pltr media-sets reference ri.mediasets.main.media-set.abc123 ri.mediasets.main.media-item.def456
```

## Transaction Management

MediaSets use transactions for uploads.

### Create Transaction

```bash
pltr media-sets create MEDIA_SET_RID [--branch BRANCH] [--preview]

# Example
pltr media-sets create ri.mediasets.main.media-set.abc123 --branch main
# Returns: Transaction ID
```

### Commit Transaction

```bash
pltr media-sets commit MEDIA_SET_RID TRANSACTION_ID [--preview] [--yes]

# Example
pltr media-sets commit ri.mediasets.main.media-set.abc123 transaction-id-12345 --yes
```

### Abort Transaction

```bash
pltr media-sets abort MEDIA_SET_RID TRANSACTION_ID [--preview] [--yes]

# Example
pltr media-sets abort ri.mediasets.main.media-set.abc123 transaction-id-12345 --yes
```

## Upload Media

```bash
pltr media-sets upload MEDIA_SET_RID FILE_PATH MEDIA_ITEM_PATH TRANSACTION_ID [--preview]

# Example
pltr media-sets upload ri.mediasets.main.media-set.abc123 \
  /local/path/image.jpg "/media/images/image.jpg" transaction-id-12345
```

## Download Media

```bash
pltr media-sets download MEDIA_SET_RID MEDIA_ITEM_RID OUTPUT_PATH [OPTIONS]

# Options:
#   --original      Download original version
#   --overwrite     Overwrite existing file
#   --preview       Enable preview mode

# Examples
pltr media-sets download ri.mediasets.main.media-set.abc123 \
  ri.mediasets.main.media-item.def456 /local/download/image.jpg

# Download original version
pltr media-sets download ri.mediasets.main.media-set.abc123 \
  ri.mediasets.main.media-item.def456 /local/download/original.jpg --original
```

## Thumbnail Operations

Generate and retrieve thumbnails for images (200px wide webp format).

### Calculate Thumbnail

Initiate thumbnail generation for an image:

```bash
pltr media-sets thumbnail-calculate MEDIA_SET_RID MEDIA_ITEM_RID [OPTIONS]

# Options:
#   --preview       Enable preview mode
#   --format        Output format (table, json, csv)
#   --output        Output file path

# Example
pltr media-sets thumbnail-calculate ri.mediasets.main.media-set.abc123 \
  ri.mediasets.main.media-item.def456
```

### Retrieve Thumbnail

Download a calculated thumbnail:

```bash
pltr media-sets thumbnail-retrieve MEDIA_SET_RID MEDIA_ITEM_RID OUTPUT_PATH [OPTIONS]

# Options:
#   --preview       Enable preview mode
#   --overwrite     Overwrite existing file

# Example
pltr media-sets thumbnail-retrieve ri.mediasets.main.media-set.abc123 \
  ri.mediasets.main.media-item.def456 /local/thumbnail.webp
```

## Upload Temporary Media

Upload temporary media that will be auto-deleted after 1 hour if not persisted:

```bash
pltr media-sets upload-temp FILE_PATH [OPTIONS]

# Options:
#   --filename      Override filename for the upload
#   --attribution   Attribution string for the media
#   --preview       Enable preview mode
#   --format        Output format (table, json, csv)
#   --output        Output file path

# Example
pltr media-sets upload-temp /local/image.jpg --attribution "Photo by John Doe"
```

## MediaSets Workflow

The typical upload workflow:

```bash
MEDIA_SET="ri.mediasets.main.media-set.abc123"

# 1. Create a transaction
TRANSACTION_ID=$(pltr media-sets create $MEDIA_SET --format json | jq -r '.transaction_id')
echo "Transaction: $TRANSACTION_ID"

# 2. Upload files within the transaction
pltr media-sets upload $MEDIA_SET /local/image1.jpg "/images/image1.jpg" $TRANSACTION_ID
pltr media-sets upload $MEDIA_SET /local/image2.jpg "/images/image2.jpg" $TRANSACTION_ID
pltr media-sets upload $MEDIA_SET /local/doc.pdf "/documents/doc.pdf" $TRANSACTION_ID

# 3. Commit the transaction (makes uploads available)
pltr media-sets commit $MEDIA_SET $TRANSACTION_ID --yes

echo "Upload complete!"
```

## Common Patterns

### Upload single file
```bash
MEDIA_SET="ri.mediasets.main.media-set.abc123"

# Create transaction
TX=$(pltr media-sets create $MEDIA_SET --format json | jq -r '.transaction_id')

# Upload
pltr media-sets upload $MEDIA_SET /path/to/file.jpg "/uploads/file.jpg" $TX

# Commit
pltr media-sets commit $MEDIA_SET $TX --yes
```

### Batch upload with error handling
```bash
MEDIA_SET="ri.mediasets.main.media-set.abc123"
TX=$(pltr media-sets create $MEDIA_SET --format json | jq -r '.transaction_id')

# Upload multiple files
for file in /local/images/*.jpg; do
  filename=$(basename "$file")
  if pltr media-sets upload $MEDIA_SET "$file" "/images/$filename" $TX; then
    echo "Uploaded: $filename"
  else
    echo "Failed: $filename"
    pltr media-sets abort $MEDIA_SET $TX --yes
    exit 1
  fi
done

# Commit if all successful
pltr media-sets commit $MEDIA_SET $TX --yes
```

### Download media by path
```bash
MEDIA_SET="ri.mediasets.main.media-set.abc123"

# Get media item RID by path
ITEM_RID=$(pltr media-sets get-by-path $MEDIA_SET "/images/photo.jpg" --format json | jq -r '.rid')

# Download
pltr media-sets download $MEDIA_SET $ITEM_RID ./downloaded_photo.jpg
```
