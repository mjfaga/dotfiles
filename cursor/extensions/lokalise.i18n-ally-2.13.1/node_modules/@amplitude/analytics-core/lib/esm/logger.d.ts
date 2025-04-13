import { LogLevel, Logger as ILogger } from '@amplitude/analytics-types';
export declare class Logger implements ILogger {
    logLevel: LogLevel;
    constructor();
    disable(): void;
    enable(logLevel?: LogLevel): void;
    log(...args: any[]): void;
    warn(...args: any[]): void;
    error(...args: any[]): void;
    debug(...args: any[]): void;
}
//# sourceMappingURL=logger.d.ts.map