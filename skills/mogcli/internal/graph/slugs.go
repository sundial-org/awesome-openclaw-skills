// Package graph provides slug ID management.
package graph

import (
	"crypto/sha256"
	"encoding/hex"
	"sync"

	"github.com/visionik/mogcli/internal/config"
)

var (
	slugCache *config.Slugs
	slugMu    sync.Mutex
)

// FormatID converts a long Microsoft Graph ID to a short slug.
func FormatID(id string) string {
	if id == "" {
		return ""
	}

	slugMu.Lock()
	defer slugMu.Unlock()

	if slugCache == nil {
		var err error
		slugCache, err = config.LoadSlugs()
		if err != nil {
			slugCache = &config.Slugs{
				IDToSlug: make(map[string]string),
				SlugToID: make(map[string]string),
			}
		}
	}

	// Check if we already have a slug for this ID
	if slug, ok := slugCache.IDToSlug[id]; ok {
		return slug
	}

	// Generate a new slug
	hash := sha256.Sum256([]byte(id))
	slug := hex.EncodeToString(hash[:])[:8]

	// Handle collisions
	origSlug := slug
	counter := 0
	for {
		if existingID, ok := slugCache.SlugToID[slug]; !ok || existingID == id {
			break
		}
		counter++
		slug = origSlug[:6] + hex.EncodeToString([]byte{byte(counter)})[:2]
	}

	// Store the mapping
	slugCache.IDToSlug[id] = slug
	slugCache.SlugToID[slug] = id

	// Save to disk (ignore errors for performance)
	_ = config.SaveSlugs(slugCache)

	return slug
}

// ResolveID converts a slug or full ID back to a full ID.
func ResolveID(input string) string {
	if input == "" {
		return ""
	}

	// If it looks like a full ID (long), return as-is
	if len(input) > 16 {
		return input
	}

	slugMu.Lock()
	defer slugMu.Unlock()

	if slugCache == nil {
		var err error
		slugCache, err = config.LoadSlugs()
		if err != nil {
			return input
		}
	}

	// Try to resolve as a slug
	if fullID, ok := slugCache.SlugToID[input]; ok {
		return fullID
	}

	// Return as-is (might be a short ID that we haven't seen)
	return input
}

// ClearSlugs clears the slug cache.
func ClearSlugs() error {
	slugMu.Lock()
	defer slugMu.Unlock()

	slugCache = &config.Slugs{
		IDToSlug: make(map[string]string),
		SlugToID: make(map[string]string),
	}

	return config.SaveSlugs(slugCache)
}
