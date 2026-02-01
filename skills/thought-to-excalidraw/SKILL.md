---
name: pm-visualizer
description: Visualizes Product Manager thoughts (Why, What, How, User Journey) into an editable Excalidraw diagram. Use when the user asks to "visualize specs", "create a PM diagram", or "map out product thoughts".
---

# PM Visualizer Skill

This skill converts unstructured Product Manager thoughts into a structured Excalidraw visualization.

## Features
- **Smart Layout**: Automatically columns "Why, What, How" and creates a horizontal flow for "User Journey".
- **Color Coding**: Visual distinction between problem (Why - Yellow), solution (What - Green), implementation (How - Blue), and flow (Journey - Red/Pink).
- **Grouped Elements**: Text is properly bound to containers so they move together.

## Workflow

1.  **Analyze Request**: Extract the following sections from the user's prompt or context:
    *   **Title**: The feature or product name.
    *   **Why**: The problem statement, business goals, or "Why are we building this?".
    *   **What**: The solution requirements, features, or "What is it?".
    *   **How**: Technical implementation details, API strategy, or "How will we build it?".
    *   **Journey**: A sequential list of steps for the user journey or process flow.

2.  **Prepare Data**: Create a JSON file (e.g., `temp_visual_data.json`) with this structure:
    ```json
    {
      "title": "Feature Name",
      "why": ["Reason 1", "Reason 2"],
      "what": ["Feature 1", "Feature 2"],
      "how": ["Tech 1", "Tech 2"],
      "journey": ["Step 1", "Step 2", "Step 3"]
    }
    ```

3.  **Generate Diagram**: Run the python script to generate the `.excalidraw` file.
    ```bash
    python3 skills/pm-visualizer/scripts/layout_diagram.py temp_visual_data.json ~/Downloads/Documents/PM_Visuals/Output_Name.excalidraw
    ```
    *Ensure the output directory exists first.*

4.  **Cleanup**: Delete the temporary JSON input file.

5.  **Report**: Inform the user the file is ready at the output path.

## Example

**User:** "Visualize a new 'Login with Google' feature. Why? Reduce friction. What? Google button on login page. How? OAuth2. Journey: User clicks button -> Google Popup -> Redirect to Dashboard."

**Codex Action:**
1.  Create `login_spec.json`:
    ```json
    {
      "title": "Login with Google",
      "why": ["Reduce friction", "Increase conversion"],
      "what": ["Google Sign-in Button", "Profile Sync"],
      "how": ["OAuth 2.0 Flow", "Google Identity SDK"],
      "journey": ["User clicks 'Sign in with Google'", "Google permissions popup appears", "User approves access", "System verifies token", "User redirected to Dashboard"]
    }
    ```
2.  `mkdir -p ~/Downloads/Documents/PM_Visuals`
3.  `python3 skills/pm-visualizer/scripts/layout_diagram.py login_spec.json ~/Downloads/Documents/PM_Visuals/Login_Spec.excalidraw`
