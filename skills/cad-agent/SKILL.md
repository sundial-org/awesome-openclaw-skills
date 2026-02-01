# CAD Agent

> Give your AI agent eyes for CAD work.

## Description

CAD Agent is a rendering server that lets AI agents see what they're building. Send modeling commands → receive rendered images → iterate visually.

**Use when:** designing 3D-printable parts, parametric CAD, mechanical design, build123d modeling

## Architecture

**Critical:** All CAD logic runs inside the container. You (the agent) only:
1. Send commands via HTTP
2. View the returned images
3. Decide what to do next

```
YOU (agent)                     CAD AGENT CONTAINER
─────────────                   ───────────────────
Send build123d code      →      Executes modeling
                         ←      Returns JSON status
Request render           →      VTK renders the model
                         ←      Returns PNG image
*Look at the image*
Decide: iterate or done
```

**Never** do STL manipulation, mesh processing, or rendering outside the container. The container handles everything — you just command and observe.

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/clawd-maf/cad-agent.git
cd cad-agent
```

### 2. Build the Docker Image

```bash
docker build -t cad-agent:latest .
```

Or using docker-compose:

```bash
docker-compose build
```

### 3. Run the Server

```bash
# Using docker-compose (recommended)
docker-compose up -d

# Or using docker directly
docker run -d --name cad-agent -p 8123:8123 cad-agent:latest serve
```

### 4. Verify Installation

```bash
curl http://localhost:8123/health
# Should return: {"status": "healthy", ...}
```

> **Docker-in-Docker caveat:** In nested container environments (e.g., Clawdbot sandbox), host networking may not work—`curl localhost:8123` will fail even though the server binds to `0.0.0.0:8123`. Use `docker exec cad-agent python3 -c "..."` commands instead. On a normal Docker host, localhost access works fine.

## Workflow

### 1. Create Model

```bash
curl -X POST http://localhost:8123/model/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_part",
    "code": "from build123d import *\nresult = Box(60, 40, 30)"
  }'
```

### 2. Render & View

```bash
# Get multi-view (front/right/top/iso)
curl -X POST http://localhost:8123/render/multiview \
  -d '{"model_name": "my_part"}' -o views.png

# Or 3D isometric
curl -X POST http://localhost:8123/render/3d \
  -d '{"model_name": "my_part", "view": "isometric"}' -o iso.png
```

**Look at the image.** Does it look right? If not, modify and re-render.

### 3. Iterate

```bash
curl -X POST http://localhost:8123/model/modify \
  -d '{
    "name": "my_part", 
    "code": "result = result - Cylinder(5, 50).locate(Pos(20, 10, 0))"
  }'

# Re-render to check
curl -X POST http://localhost:8123/render/3d \
  -d '{"model_name": "my_part"}' -o updated.png
```

### 4. Export

```bash
curl -X POST http://localhost:8123/export \
  -d '{"model_name": "my_part", "format": "stl"}' -o part.stl
```

## Endpoints

| Endpoint | What it does |
|----------|--------------|
| `POST /model/create` | Run build123d code, create model |
| `POST /model/modify` | Modify existing model |
| `GET /model/list` | List models in session |
| `GET /model/{name}/measure` | Get dimensions |
| `POST /render/3d` | 3D shaded render (VTK) |
| `POST /render/2d` | 2D technical drawing |
| `POST /render/multiview` | 4-view composite |
| `POST /export` | Export STL/STEP/3MF |
| `POST /analyze/printability` | Check if printable |

## build123d Cheatsheet

```python
from build123d import *

# Primitives
Box(width, depth, height)
Cylinder(radius, height)
Sphere(radius)

# Boolean
a + b   # union
a - b   # subtract
a & b   # intersect

# Position
part.locate(Pos(x, y, z))
part.rotate(Axis.Z, 45)

# Edges
fillet(part.edges(), radius)
chamfer(part.edges(), length)
```

## Important

- **Don't bypass the container.** No matplotlib, no external STL libraries, no mesh hacking.
- **Renders are your eyes.** Always request a render after changes.
- **Iterate visually.** The whole point is you can see what you're building.

## Design File Safety

The project has safeguards against accidentally committing CAD outputs:
- `.gitignore` blocks *.stl, *.step, *.3mf, etc.
- Pre-commit hook rejects design files
- User's designs stay local, never versioned

## Links

- [Repository](https://github.com/clawd-maf/cad-agent)
- [build123d docs](https://build123d.readthedocs.io/)
- [VTK](https://vtk.org/)
