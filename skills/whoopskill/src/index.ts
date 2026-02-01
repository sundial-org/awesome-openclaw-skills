#!/usr/bin/env node

import { config } from 'dotenv';
import { program } from './cli.js';

config();

program.parse();
