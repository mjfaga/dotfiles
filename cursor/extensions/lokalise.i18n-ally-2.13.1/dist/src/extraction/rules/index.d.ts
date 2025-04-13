import { BasicExtrationRule } from './basic';
import { NonAsciiExtractionRule } from './non-ascii-characters';
import { DynamicExtractionRule } from './dynamic';
export * from './base';
export * from './basic';
export * from './non-ascii-characters';
export declare const DefaultExtractionRules: (BasicExtrationRule | NonAsciiExtractionRule)[];
export declare const DefaultDynamicExtractionsRules: DynamicExtractionRule[];
