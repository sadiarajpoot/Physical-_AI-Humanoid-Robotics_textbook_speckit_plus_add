# Quickstart Guide: AI/Spec-Driven Textbook for Physical AI & Humanoid Robotics

## Prerequisites

- Node.js (LTS version recommended)
- npm or yarn package manager
- Git
- Text editor (VS Code recommended)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Install Dependencies
```bash
npm install
# OR
yarn install
```

### 3. Initialize Docusaurus Project
```bash
npx create-docusaurus@latest textbook-physical-ai classic --typescript
cd textbook-physical-ai
```

### 4. Set up Project Structure
```bash
# Create content directories
mkdir -p docs/modules
mkdir -p docs/weekly-breakdown
mkdir -p docs/hardware
mkdir -p docs/assessments
mkdir -p docs/technical-examples
```

## Development Workflow

### 1. Start Development Server
```bash
npm start
# OR
yarn start
```
This command starts a local development server and opens the application in your browser at `http://localhost:3000`.

### 2. Add Content
- Add new content files to the appropriate directories
- Update `sidebars.js` to include new pages in navigation
- Use proper Markdown formatting with headings, lists, and tables

### 3. Content Creation Process
1. Define content specs using Spec-Kit Plus
2. Generate content with Claude Code assistance where appropriate
3. Ensure all content originates from the provided course document
4. Validate Markdown formatting and table rendering
5. Test responsive design on different screen sizes

### 4. Build for Production
```bash
npm run build
# OR
yarn build
```
This command generates static content into the `build` directory and can be served using any static content hosting service.

## Content Organization

### Directory Structure
```
docs/
├── index.md              # Homepage
├── overview/             # Quarter Overview, Why Physical AI Matters
├── learning-outcomes/    # Learning Outcomes section
├── modules/              # Modules 1-4
├── weekly-breakdown/     # Weekly Breakdown (Weeks 1-13)
├── capstone/             # Capstone Project
├── assessments/          # Assessments
├── hardware/             # Hardware Requirements
└── technical-examples/   # ROS 2, Gazebo setups, etc.
```

### Navigation Structure
The sidebar navigation is organized as:
- Modules (Module 1-4)
- Weekly Breakdown (Weeks 1-13)
- Hardware Requirements
- Other sections as needed

## Deployment

### GitHub Pages
1. Configure your GitHub repository for GitHub Pages
2. Set the source to the `gh-pages` branch or `/docs` folder
3. Run the build command and push to the appropriate branch

### Vercel
1. Connect your GitHub repository to Vercel
2. Set the build command to `npm run build` or `yarn build`
3. Set the output directory to `build`

## Testing

### Local Testing
- Verify all navigation works correctly
- Check responsive design on different screen sizes
- Validate all content renders properly
- Test search functionality

### Content Validation
- Ensure 100% of original course document is included
- Verify all hardware requirement tables render correctly
- Check that technical examples are properly formatted
- Confirm no external content has been added

## Key Commands

| Command | Description |
|---------|-------------|
| `npm start` | Start local development server |
| `npm run build` | Build static files for production |
| `npm run serve` | Serve the built site locally |
| `npm run docusaurus` | Show all available commands |

## Troubleshooting

### Common Issues
1. **Content not appearing**: Check that the file is added to `sidebars.js`
2. **Formatting issues**: Verify Markdown syntax and proper headings
3. **Build errors**: Check for missing dependencies or syntax errors
4. **Responsive issues**: Test on multiple screen sizes during development

### Performance Tips
- Optimize images for web
- Use proper heading hierarchy (h1, h2, h3, etc.)
- Keep Markdown files organized and well-structured
- Use Docusaurus features like admonitions and code blocks appropriately