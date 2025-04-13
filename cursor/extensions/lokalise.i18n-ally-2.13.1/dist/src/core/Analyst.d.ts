import { Location, EventEmitter } from 'vscode';
import { UsageReport } from './types';
import { KeyOccurrence } from '.';
export declare class Analyst {
    private static _cache;
    static readonly _onDidUsageReportChanged: EventEmitter<UsageReport>;
    static readonly onDidUsageReportChanged: import("vscode").Event<UsageReport>;
    static invalidateCache(): void;
    static invalidateCacheOf(filepath: string): void;
    static watch(): import("vscode").Disposable;
    static hasCache(): boolean;
    static refresh(): void;
    private static updateCache;
    private static enumerateDocumentPaths;
    private static getOccurrencesOfFile;
    private static getOccurrencesOfText;
    static getAllOccurrences(targetKey?: string, useCache?: boolean): Promise<KeyOccurrence[]>;
    static getAllOccurrenceLocations(targetKey: string): Promise<Location[]>;
    static getLocationOf(occurrence: KeyOccurrence): Promise<Location>;
    static normalizeKey(key: string): string;
    static analyzeUsage(useCache?: boolean): Promise<UsageReport>;
}
