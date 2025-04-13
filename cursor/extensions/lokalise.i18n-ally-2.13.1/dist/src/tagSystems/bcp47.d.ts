import { BaseTagSystem } from './base';
export declare class BCP47 extends BaseTagSystem {
    normalize(locale?: string, fallback?: string, strict?: boolean): string;
    toBCP47(locale: string): string | undefined;
    toFlagname(locale: string): string;
    lookup(locale: string): string;
}
