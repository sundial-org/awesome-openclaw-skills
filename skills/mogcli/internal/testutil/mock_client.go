// Package testutil provides testing utilities for mogcli.
package testutil

import (
	"context"
	"net/url"
)

// MockClient implements graph.Client for testing.
type MockClient struct {
	GetFunc     func(ctx context.Context, path string, query url.Values) ([]byte, error)
	PostFunc    func(ctx context.Context, path string, body interface{}) ([]byte, error)
	PatchFunc   func(ctx context.Context, path string, body interface{}) ([]byte, error)
	DeleteFunc  func(ctx context.Context, path string) error
	PostHTMLFunc func(ctx context.Context, path string, html string) ([]byte, error)
	PutFunc     func(ctx context.Context, path string, data []byte, contentType string) ([]byte, error)
}

// Get implements graph.Client.Get.
func (m *MockClient) Get(ctx context.Context, path string, query url.Values) ([]byte, error) {
	if m.GetFunc != nil {
		return m.GetFunc(ctx, path, query)
	}
	return nil, nil
}

// Post implements graph.Client.Post.
func (m *MockClient) Post(ctx context.Context, path string, body interface{}) ([]byte, error) {
	if m.PostFunc != nil {
		return m.PostFunc(ctx, path, body)
	}
	return nil, nil
}

// Patch implements graph.Client.Patch.
func (m *MockClient) Patch(ctx context.Context, path string, body interface{}) ([]byte, error) {
	if m.PatchFunc != nil {
		return m.PatchFunc(ctx, path, body)
	}
	return nil, nil
}

// Delete implements graph.Client.Delete.
func (m *MockClient) Delete(ctx context.Context, path string) error {
	if m.DeleteFunc != nil {
		return m.DeleteFunc(ctx, path)
	}
	return nil
}

// PostHTML implements graph.Client.PostHTML.
func (m *MockClient) PostHTML(ctx context.Context, path string, html string) ([]byte, error) {
	if m.PostHTMLFunc != nil {
		return m.PostHTMLFunc(ctx, path, html)
	}
	return nil, nil
}

// Put implements graph.Client.Put.
func (m *MockClient) Put(ctx context.Context, path string, data []byte, contentType string) ([]byte, error) {
	if m.PutFunc != nil {
		return m.PutFunc(ctx, path, data, contentType)
	}
	return nil, nil
}
