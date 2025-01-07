export interface TechnologyInfo {
  name: string;
  type: string;
  category: string;
  description: string;
  popularity?: Record<string, any>;
  version_info?: Record<string, any>;
  ecosystem?: Record<string, string[]>;
  use_cases?: string[];
}

class TriggerMap {
  private technologies: Map<string, TechnologyInfo>;
  private patternString: string;

  constructor() {
    this.technologies = new Map();
    this.initializeTechnologies();
    this.patternString = this.buildPatternString();
  }

  private initializeTechnologies() {
    // Languages
    this.addTechnology({
      name: 'python',
      type: 'language',
      category: 'backend',
      description: 'A versatile programming language'
    });
    this.addTechnology({
      name: 'javascript',
      type: 'language',
      category: 'frontend',
      description: 'A web programming language'
    });
    this.addTechnology({
      name: 'typescript',
      type: 'language',
      category: 'frontend',
      description: 'A typed superset of JavaScript'
    });

    // Frontend Frameworks
    this.addTechnology({
      name: 'react',
      type: 'framework',
      category: 'frontend',
      description: 'A JavaScript library for building user interfaces'
    });
    this.addTechnology({
      name: 'angular',
      type: 'framework',
      category: 'frontend',
      description: 'A TypeScript-based web application framework'
    });
    this.addTechnology({
      name: 'vue',
      type: 'framework',
      category: 'frontend',
      description: 'A progressive JavaScript framework'
    });

    // Backend Frameworks
    this.addTechnology({
      name: 'node.js',
      type: 'framework',
      category: 'backend',
      description: 'A JavaScript runtime environment'
    });
    this.addTechnology({
      name: 'django',
      type: 'framework',
      category: 'backend',
      description: 'A high-level Python web framework'
    });
    this.addTechnology({
      name: 'flask',
      type: 'framework',
      category: 'backend',
      description: 'A lightweight Python web framework'
    });

    // Databases
    this.addTechnology({
      name: 'mongodb',
      type: 'database',
      category: 'database',
      description: 'A NoSQL database'
    });
    this.addTechnology({
      name: 'postgresql',
      type: 'database',
      category: 'database',
      description: 'A relational database'
    });
    this.addTechnology({
      name: 'mysql',
      type: 'database',
      category: 'database',
      description: 'A relational database management system'
    });

    // Testing Frameworks
    this.addTechnology({
      name: 'jest',
      type: 'framework',
      category: 'testing',
      description: 'A JavaScript testing framework'
    });
    this.addTechnology({
      name: 'pytest',
      type: 'framework',
      category: 'testing',
      description: 'A Python testing framework'
    });

    // DevOps Tools
    this.addTechnology({
      name: 'docker',
      type: 'tool',
      category: 'devops',
      description: 'A containerization platform'
    });
    this.addTechnology({
      name: 'kubernetes',
      type: 'tool',
      category: 'devops',
      description: 'A container orchestration system'
    });
  }

  private addTechnology(tech: TechnologyInfo) {
    this.technologies.set(tech.name.toLowerCase(), tech);
  }

  private buildPatternString(): string {
    const patterns = Array.from(this.technologies.keys());
    return `\\b(${patterns.join('|')})\\b`;
  }

  get pattern(): RegExp {
    return new RegExp(this.patternString, 'gi');
  }

  getTechnology(name: string): TechnologyInfo | undefined {
    return this.technologies.get(name.toLowerCase());
  }

  getAllTechnologies(): TechnologyInfo[] {
    return Array.from(this.technologies.values());
  }
}

export const TRIGGER_MAP = new TriggerMap();
