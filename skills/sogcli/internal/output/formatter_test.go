package output

import (
	"bytes"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestFormatterJSON(t *testing.T) {
	var buf bytes.Buffer
	f := New(&buf, true, false)

	data := map[string]any{
		"name":  "test",
		"count": 42,
	}

	err := f.Print(data)
	require.NoError(t, err)

	assert.Contains(t, buf.String(), `"name": "test"`)
	assert.Contains(t, buf.String(), `"count": 42`)
}

func TestFormatterPlainMap(t *testing.T) {
	var buf bytes.Buffer
	f := New(&buf, false, true)

	data := map[string]any{
		"key": "value",
	}

	err := f.Print(data)
	require.NoError(t, err)

	assert.Contains(t, buf.String(), "key\tvalue")
}

func TestFormatterPlainSlice(t *testing.T) {
	var buf bytes.Buffer
	f := New(&buf, false, true)

	data := []map[string]any{
		{"a": "1"},
		{"b": "2"},
	}

	err := f.Print(data)
	require.NoError(t, err)

	output := buf.String()
	assert.Contains(t, output, "1")
	assert.Contains(t, output, "2")
}

func TestFormatterHuman(t *testing.T) {
	var buf bytes.Buffer
	f := New(&buf, false, false)

	err := f.Print("hello world")
	require.NoError(t, err)

	assert.Equal(t, "hello world\n", buf.String())
}

func TestFormatterFormatSelection(t *testing.T) {
	tests := []struct {
		name   string
		json   bool
		plain  bool
		expect Format
	}{
		{"default", false, false, FormatHuman},
		{"json", true, false, FormatJSON},
		{"plain", false, true, FormatPlain},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			var buf bytes.Buffer
			f := New(&buf, tt.json, tt.plain)
			assert.Equal(t, tt.expect, f.format)
		})
	}
}
