# MCP Universal Bridge Spec

Last updated: 2026-04-14 00:05 EDT
Status: READY

## Purpose
Expose a public Model Context Protocol bridge at `/.well-known/mcp` that normalizes legacy API data into agent-ready JSON.

## Core functions
- schema normalization
- auth boundary separation
- stable JSON envelopes
- health and capability discovery
- error translation for 404/500 upstream failures

## Endpoint surfaces
- `/.well-known/mcp`
- `/health`
- `/translate`
- `/capabilities`

## Safety posture
- no secret leakage
- no implicit write-through to third-party systems
- bounded transforms only

## Suggested implementation
- FastAPI service
- JSON schema validation
- structured error objects
- optional x402-compatible gate kept separate from core transport logic
