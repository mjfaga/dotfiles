import { Storage } from '@amplitude/analytics-types';
export declare class MemoryStorage<T> implements Storage<T> {
    memoryStorage: Map<string, T>;
    isEnabled(): Promise<boolean>;
    get(key: string): Promise<T | undefined>;
    getRaw(key: string): Promise<string | undefined>;
    set(key: string, value: T): Promise<void>;
    remove(key: string): Promise<void>;
    reset(): Promise<void>;
}
//# sourceMappingURL=memory.d.ts.map