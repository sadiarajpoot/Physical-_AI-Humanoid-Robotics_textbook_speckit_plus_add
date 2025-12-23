<!-- SYNC IMPACT REPORT
     Version change: 1.2.0 → 1.3.0
     Added sections: UI Integration Focus, Responsive Design Priority, Claude Subagents/Agent Skills Integration, Better-Auth UI Implementation, Per-Chapter Personalization, Per-Chapter Urdu Translation
     Removed sections: None
     Templates requiring updates:
       - .specify/templates/plan-template.md ⚠ pending
       - .specify/templates/spec-template.md ⚠ pending
       - .specify/templates/tasks-template.md ⚠ pending
     Modified principles: Updated all principles to reflect UI Integration focus with RAG Chatbot
     Follow-up TODOs: None
-->

# UI Integration for Unified Textbook and RAG Chatbot on Physical AI & Humanoid Robotics Constitution

## Core Principles

### Seamless UI Integration
Seamless embedding of RAG chatbot within the Docusaurus textbook for intuitive user experience. The chatbot interface must be naturally integrated into the textbook layout without disrupting the reading experience, providing contextual assistance while maintaining educational flow and visual consistency with the textbook design.

### Responsive Design Priority
Responsive design ensuring usability across devices (desktop, tablet, mobile) with equal functionality and user experience. The integrated UI must adapt seamlessly to different screen sizes and orientations while maintaining all core features including chatbot interaction, personalization options, and translation capabilities without degradation of functionality.

### Hackathon Requirements Fidelity
Strict adherence to hackathon requirements: implementation of base functionality plus all bonus features for maximum scoring potential. The UI must support all required features including dual query modes, authentication, personalization, and multilingual capabilities while ensuring the 90-second demo showcases all functionality effectively.

### Educational Enhancement Through Interactivity
Educational enhancement through interactive, personalized, and multilingual features that improve learning outcomes. The UI must provide intuitive access to personalization and translation features per chapter, enabling students to customize their learning experience while maintaining focus on educational content and accessibility.

### Robust Integration Without Performance Degradation
Integration of all components without compromising textbook performance or chatbot accuracy. The UI implementation must maintain fast loading times, smooth interactions, and responsive chatbot functionality while supporting all bonus features and maintaining cross-browser compatibility and accessibility standards.

## Key Standards and Implementation Guidelines

Frontend development with Docusaurus and custom React components for chatbot UI, buttons, and responsive layouts ensuring seamless integration with textbook content. Backend integration using FastAPI endpoints called via fetch/Axios from frontend with proper error handling and timeout management. Responsive design implementation using CSS media queries, flex/grid layouts, and Docusaurus themes for optimal mobile-friendliness. Chatbot embedding as persistent chat window or sidebar that handles both book-wide and selected-text queries with intuitive user interface. Claude Subagents/Agent Skills integration for dynamic UI elements providing up to 50 bonus points through intelligent interface components. Better-Auth UI implementation for signup/signin with background questions providing up to 50 bonus points through enhanced user profiling. Per-chapter personalization button implementing content adaptation with responsive UI providing up to 50 bonus points through customized learning experience. Per-chapter Urdu translation button implementing localized text rendering with responsive UI providing up to 50 bonus points through multilingual accessibility. Cross-browser compatibility and accessibility implementation with proper ARIA labels and semantic HTML for inclusive design. Integration within monorepo structure with existing frontend/backend folders maintaining code organization and deployment simplicity.

## Constraints and Boundaries

Monorepo integration in existing frontend/backend folders without disrupting current architecture or requiring major structural changes. Exclusive use of Gemini API for all AI-driven UI features including translations and personalization without alternative AI service integration. Cross-browser compatibility requirement supporting major browsers (Chrome, Firefox, Safari, Edge) with consistent functionality and appearance. Accessibility compliance with ARIA labels and semantic HTML implementation for inclusive user experience. Unified deployment to GitHub Pages/Vercel with responsive layout maintained across all deployment environments. Timeline constraint requiring completion post-textbook and chatbot setup but before hackathon submission deadline. Integration must not compromise existing textbook functionality or performance metrics.

## Success Criteria

Fully responsive textbook with embedded chatbot working seamlessly on all target devices (desktop, tablet, mobile) with consistent user experience. All query modes (book-wide, selected-text) fully functional within the UI with intuitive access and clear visual feedback. Bonus features (Claude Subagents, Better-Auth, personalization, translation) integrated with responsive UIs including forms, buttons, and dynamic content that enhance rather than complicate the user experience. Hackathon demo under 90 seconds showcasing all responsive features, integration quality, and bonus implementations with clear demonstration of value to judges. Project achieves base 100 points plus up to 200 bonus points through successful implementation of all specified features. UI maintains textbook performance standards while adding all requested functionality without degradation of user experience.

## Governance

This constitution governs all aspects of the UI Integration for Unified Textbook and RAG Chatbot on Physical AI & Humanoid Robotics project. All development activities must comply with the core principles and implementation guidelines outlined above. Any deviation from these principles requires formal amendment to this constitution. All team members must verify compliance with these principles during code reviews and quality gates, particularly focusing on UI/UX consistency, responsive design standards, and integration quality. Development must follow the established workflow with proper spec-driven development practices and comprehensive testing of UI components across all target devices and browsers. All UI implementations must prioritize user experience and accessibility while maintaining the educational focus of the textbook content.

**Version**: 1.3.0 | **Ratified**: 2024-12-18 | **Last Amended**: 2025-12-20