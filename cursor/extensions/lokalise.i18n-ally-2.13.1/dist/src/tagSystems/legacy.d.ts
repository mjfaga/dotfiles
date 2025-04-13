import { BaseTagSystem } from './base';
export declare class LegacyTagSystem extends BaseTagSystem {
    normalize(locale?: string, fallback?: string, strict?: boolean): any;
    toFlagname(locale: string): string;
}
