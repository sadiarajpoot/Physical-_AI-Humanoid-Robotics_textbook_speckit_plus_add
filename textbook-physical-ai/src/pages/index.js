import React, { useEffect } from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <div className={styles.heroContent}>
          {/* Left side animation */}
          <div className={styles.leftAnimation}>
            <div className={styles.aiParticles}>
              <div className={styles.particle}></div>
              <div className={styles.particle}></div>
              <div className={styles.particle}></div>
            </div>
            <div className={styles.neuralNetwork}></div>
          </div>

          <div className={styles.heroText}>
            <h1 className={clsx('hero__title', styles.animatedTitle)}>
              {siteConfig.title}
            </h1>
            <p className={clsx('hero__subtitle', styles.heroSubtitle)}>
              {siteConfig.tagline}
            </p>
            <p className={styles.heroDescription}>
              Advanced Physical AI, Robotics Intelligence & Human-like Motion
            </p>
            <div className={styles.heroButtons}>
              <Link
                className={clsx('button button--secondary button--lg', styles.heroButton)}
                to="/docs/intro">
                Start Learning
              </Link>
              <Link
                className={clsx('button button--primary button--lg', styles.heroButton)}
                to="#modules">
                Explore Modules
              </Link>
            </div>
          </div>

          {/* Right side animation */}
          <div className={styles.rightAnimation}>
            <div className={styles.aiParticles}>
              <div className={styles.particle}></div>
              <div className={styles.particle}></div>
              <div className={styles.particle}></div>
            </div>
            <div className={styles.neuralNetwork}></div>
          </div>
        </div>
      </div>
    </header>
  );
}

function ModuleCard({title, description, index, image}) {
  return (
    <div className={clsx(styles.moduleCard, 'col col--3')} data-aos="fade-up" data-aos-delay={index * 100}>
      <Link to={`/docs/modules/module-${index + 1}`} className={styles.moduleCardLink}>
        <div className={styles.moduleCardContent}>
          <div className={styles.moduleCardImage}>
            <img
              src={image}
              alt={title}
              className={styles.moduleCardImg}
              onError={(e) => {
                e.target.src = 'https://images.unsplash.com/photo-1581092580497-e0d23cbdf1dc?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80';
              }}
            />
            <div className={styles.imageOverlay}></div>
          </div>
          <div className={styles.moduleCardInfo}>
            <h3 className={styles.moduleCardTitle}>{title}</h3>
            <p className={styles.moduleCardDescription}>{description}</p>
          </div>
          <div className={styles.moduleCardHover}></div>
        </div>
      </Link>
    </div>
  );
}

function useScrollAnimation() {
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add(styles['aos-animate']);
          }
        });
      },
      {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
      }
    );

    const elements = document.querySelectorAll('[data-aos="fade-up"]');
    elements.forEach((el) => observer.observe(el));

    return () => {
      elements.forEach((el) => observer.unobserve(el));
    };
  }, []);
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();

  useScrollAnimation();

  const modules = [
    {
      title: "Module 1: Foundations of Physical AI",
      description: "Core concepts of Physical AI, embodied intelligence, and the theoretical foundations of robot-environment interaction.",
      image: "https://images.unsplash.com/photo-1581092580497-e0d23cbdf1dc?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80"
    },
    {
      title: "Module 2: Sensors, Actuators & Perception",
      description: "Advanced sensor systems, actuator control, and real-time feedback mechanisms for robotic systems.",
      image: "https://images.unsplash.com/photo-1560250097-0b93528c311a?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80"
    },
    {
      title: "Module 3: Humanoid Robotics Systems",
      description: "Biomechanics of human-like movement, perception systems, and dynamic balance control.",
      image: "https://images.unsplash.com/photo-1622367768513-ce802e3f0e0d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80"
    },
    {
      title: "Module 4: Intelligence, Control & Human Interaction",
      description: "Machine learning, neural networks, and AI algorithms that power autonomous robotic decision-making.",
      image: "https://images.unsplash.com/photo-1550745165-9bc0b252726f?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80"
    }
  ];

function Footer() {
  return (
    <footer className={styles.footer}>
      <div className="container">
        <div className={styles.footerGrid}>
          <div className={styles.footerSection}>
            <h3>📚 Course Content</h3>
            <ul>
              <li><Link to="/docs/intro">Introduction</Link></li>
              <li><Link to="/docs/modules/module-1">Module 1: Foundations</Link></li>
              <li><Link to="/docs/modules/module-2">Module 2: Sensors & Perception</Link></li>
              <li><Link to="/docs/modules/module-3">Module 3: Humanoid Systems</Link></li>
              <li><Link to="/docs/modules/module-4">Module 4: AI & Control</Link></li>
            </ul>
          </div>
          <div className={styles.footerSection}>
            <h3>🎓 Learning Resources</h3>
            <ul>
              <li><Link to="/docs/capstone">Capstone Project</Link></li>
              <li><Link to="/docs/assessments">Assessments</Link></li>
              <li><Link to="/docs/learning-outcomes">Learning Outcomes</Link></li>
            </ul>
          </div>
          <div className={styles.footerSection}>
            <h3>🛠️ Development Tools</h3>
            <ul>
              <li><a href="https://docs.ros.org/" target="_blank" rel="noopener noreferrer">ROS 2 Documentation</a></li>
              <li><a href="https://gazebosim.org/" target="_blank" rel="noopener noreferrer">Gazebo Simulator</a></li>
              <li><a href="https://developer.nvidia.com/isaac" target="_blank" rel="noopener noreferrer">NVIDIA Isaac</a></li>
              <li><a href="https://pybullet.org/" target="_blank" rel="noopener noreferrer">PyBullet Physics</a></li>
              <li><a href="https://openai.com/research/robotics" target="_blank" rel="noopener noreferrer">OpenAI Robotics</a></li>
            </ul>
          </div>
          <div className={styles.footerSection}>
            <h3>📞 Connect With Us</h3>
            <p>For academic inquiries and support</p>
            <p className={styles.footerContact}>
              <a href="mailto:contact@example.com">contact@example.com</a>
            </p>
            <div className={styles.footerSocial}>
              <a href="https://github.com" aria-label="GitHub">🐙</a>
              <a href="https://twitter.com" aria-label="Twitter">🐦</a>
              <a href="https://linkedin.com" aria-label="LinkedIn">👔</a>
            </div>
          </div>
        </div>
        <div className={styles.footerBottom}>
          <p className={styles.copyright}>
            © {new Date().getFullYear()} Physical AI & Humanoid Robotics Book. All rights reserved. Built with Docusaurus.
          </p>
        </div>
      </div>
    </footer>
  );
}

  return (
    <Layout
      title={`Welcome to ${siteConfig.title}`}
      description="Physical AI & Humanoid Robotics - An Interactive Book for AI and Computer Science Students">
      <HomepageHeader />
      <main>
        <section id="modules" className={styles.modulesSection}>
          <div className="container">
            <h2 className={styles.sectionTitle}>Core Modules</h2>
            <p className={styles.sectionSubtitle}>Explore the fundamental building blocks of Physical AI & Robotics</p>
            <div className="row">
              {modules.map((module, index) => (
                <ModuleCard
                  key={index}
                  title={module.title}
                  description={module.description}
                  image={module.image}
                  index={index}
                />
              ))}
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </Layout>
  );
}