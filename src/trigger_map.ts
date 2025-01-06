export interface TriggerInfo {
  name: string;
  type: string;
  category: string;
  description: string;
  confidence_score: number;
  popularity?: Record<string, any>;
  version_info?: Record<string, any>;
  ecosystem?: Record<string, string[]>;
  use_cases?: string[];
}

export interface TriggerMapConfig {
  caseSensitive?: boolean;
  maxPatternLength?: number;
}

export interface TriggerPattern {
  pattern: string;
  flags?: string;
  score?: number;
}

export interface TriggerResult {
  match: string;
  info: TriggerInfo;
  score: number;
}

export class TriggerMap {
  private patterns: Map<string, RegExp>;
  public technologies: Map<string, TriggerInfo>;

  constructor() {
    this.patterns = new Map();
    this.technologies = new Map();
    this.initializeTechnologies();
  }

  private initializeTechnologies() {
    // Frontend Frameworks
    this.addTechnology('react', {
      name: 'React',
      type: 'framework',
      category: 'frontend',
      description: 'A JavaScript library for building user interfaces',
      confidence_score: 0.9,
      ecosystem: {
        related: ['react-dom', 'react-router', 'redux']
      }
    });

    this.addTechnology('angular', {
      name: 'Angular',
      type: 'framework',
      category: 'frontend',
      description: 'A platform for building web applications',
      confidence_score: 0.9,
      ecosystem: {
        related: ['rxjs', '@angular/core', '@angular/cli']
      }
    });

    // Backend Technologies
    this.addTechnology('node', {
      name: 'Node.js',
      type: 'platform',
      category: 'backend',
      description: 'JavaScript runtime built on Chrome\'s V8 JavaScript engine',
      confidence_score: 0.9,
      ecosystem: {
        related: ['npm', 'express', 'koa']
      }
    });

    this.addTechnology('express', {
      name: 'Express',
      type: 'framework',
      category: 'backend',
      description: 'Fast, unopinionated, minimalist web framework for Node.js',
      confidence_score: 0.9,
      ecosystem: {
        related: ['body-parser', 'morgan', 'cors']
      }
    });

    // Databases
    this.addTechnology('mongodb', {
      name: 'MongoDB',
      type: 'database',
      category: 'database',
      description: 'NoSQL database program',
      confidence_score: 0.9,
      ecosystem: {
        related: ['mongoose', 'mongodb-client']
      }
    });

    // Languages
    this.addTechnology('typescript', {
      name: 'TypeScript',
      type: 'language',
      category: 'language',
      description: 'Typed superset of JavaScript',
      confidence_score: 0.9,
      ecosystem: {
        related: ['ts-node', 'tsc', '@types']
      }
    });

    // Testing
    this.addTechnology('jest', {
      name: 'Jest',
      type: 'tool',
      category: 'testing',
      description: 'JavaScript Testing Framework',
      confidence_score: 0.9,
      ecosystem: {
        related: ['ts-jest', '@testing-library/react']
      }
    });
  }

  private addTechnology(key: string, info: TriggerInfo) {
    this.technologies.set(key.toLowerCase(), info);
    this.patterns.set(
      key,
      new RegExp(`\\b${key}\\b`, 'gi')
    );
  }

  public get pattern(): RegExp {
    const patterns = Array.from(this.patterns.values())
      .map(p => p.source.slice(2, -2)) // Remove \b boundaries
      .join('|');
    return new RegExp(`\\b(${patterns})\\b`, 'gi');
  }

  public getTechnology(key: string): TriggerInfo | undefined {
    return this.technologies.get(key.toLowerCase());
  }

  public getAllTechnologies(): Map<string, TriggerInfo> {
    return new Map(this.technologies);
  }
}

export const TRIGGER_MAP = new TriggerMap();
