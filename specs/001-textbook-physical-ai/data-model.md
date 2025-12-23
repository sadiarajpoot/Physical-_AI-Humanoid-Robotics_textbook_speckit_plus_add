# Data Model: AI/Spec-Driven Textbook for Physical AI & Humanoid Robotics

## Entity: Textbook Content
**Description**: The comprehensive digital textbook containing all course sections

**Fields**:
- id: Unique identifier for the textbook
- title: "AI/Spec-Driven Textbook for Physical AI & Humanoid Robotics"
- sections: Array of content sections (Quarter Overview, Why Physical AI Matters, Learning Outcomes, etc.)
- modules: Array of modules (Module 1-4)
- weeklyBreakdown: Array of weekly content (Weeks 1-13)
- assessments: Array of assessment materials
- hardwareRequirements: Hardware requirements data with tables
- createdAt: Creation timestamp
- updatedAt: Last update timestamp

**Relationships**:
- Contains multiple Content Sections
- Contains multiple Modules
- Contains weekly breakdown content
- Contains assessment materials
- Contains hardware requirements

**Validation Rules**:
- All sections from the original course document must be present
- Content must originate exclusively from the provided course document
- All hardware requirement tables must be accurately rendered

## Entity: Content Section
**Description**: Individual sections of the textbook (Quarter Overview, Why Physical AI Matters, etc.)

**Fields**:
- id: Unique identifier for the section
- title: Section title
- content: Markdown content of the section
- order: Display order in the textbook
- type: Section type (overview, module, assessment, hardware, etc.)
- parentSection: Reference to parent section if applicable
- childrenSections: Array of child subsections
- createdAt: Creation timestamp
- updatedAt: Last update timestamp

**Relationships**:
- Belongs to a Textbook Content
- May have parent Section
- May contain multiple child Sections

**Validation Rules**:
- Content must be well-organized with proper Markdown formatting
- Must not contain external additions beyond the original document

## Entity: Module
**Description**: Course modules (Module 1: The Robotic Nervous System (ROS 2), Module 2: The Digital Twin (Gazebo & Unity), etc.)

**Fields**:
- id: Unique identifier for the module
- title: Module title
- number: Module number (1-4)
- content: Markdown content of the module
- learningObjectives: Array of learning objectives for the module
- technicalExamples: Array of technical examples and code snippets
- order: Display order among modules
- createdAt: Creation timestamp
- updatedAt: Last update timestamp

**Relationships**:
- Belongs to a Textbook Content
- Contains multiple Content Sections
- May contain Technical Examples

**Validation Rules**:
- Must include technical content with code examples for ROS 2, Gazebo setups, etc.
- Technical examples must be generated via Claude Code as specified

## Entity: Technical Example
**Description**: Code examples and technical implementations for ROS 2, Gazebo setups, etc.

**Fields**:
- id: Unique identifier for the example
- title: Example title
- description: Brief description of the example
- code: Code snippet content (formatted properly)
- language: Programming language (Python, C++, etc.)
- relatedModule: Reference to the related module
- createdAt: Creation timestamp
- updatedAt: Last update timestamp

**Relationships**:
- Belongs to a Module
- Referenced by Content Sections

**Validation Rules**:
- Code must be properly formatted and executable
- Must demonstrate relevant concepts (ROS 2, Gazebo, etc.)

## Entity: Hardware Requirement
**Description**: Hardware specifications and requirements tables

**Fields**:
- id: Unique identifier for the hardware requirement
- title: Hardware category title (Digital Twin Workstation, Edge Kit, Robot Options, etc.)
- tableData: Structured data for the hardware table
- specifications: Array of specific hardware specifications
- requirements: Array of requirement details
- createdAt: Creation timestamp
- updatedAt: Last update timestamp

**Relationships**:
- Belongs to a Textbook Content
- Referenced by Content Sections

**Validation Rules**:
- Tables must be accurately rendered in Markdown format
- All hardware requirement tables from the original document must be included
- Must display properly across different screen sizes

## Entity: Navigation Item
**Description**: Items in the sidebar navigation system

**Fields**:
- id: Unique identifier for the navigation item
- title: Display title in navigation
- path: URL path for the content
- order: Display order in navigation
- parent: Reference to parent navigation item
- children: Array of child navigation items
- category: Navigation category (Modules, Weekly Breakdown, Hardware)
- isVisible: Whether the item is visible in navigation
- createdAt: Creation timestamp
- updatedAt: Last update timestamp

**Relationships**:
- Points to Content Section or Module
- May have parent Navigation Item
- May contain child Navigation Items

**Validation Rules**:
- Must enable intuitive navigation with logical categorization
- Users must be able to navigate within 3 clicks as specified in success criteria