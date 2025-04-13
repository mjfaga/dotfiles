export declare abstract class BaseTagSystem {
    normalize(locale?: string, fallback?: string, strict?: boolean): string;
    toBCP47(str: string): string | undefined;
    fromBCP47(bcp47: string): string;
    toFlagname(locale: string): string | undefined;
    getFlagName(locale: string): string;
    lookup(locale: string): string | undefined;
}
