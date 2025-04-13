declare function hasCache(key: string): boolean;
declare function setCache<T>(key: string, value: T): T;
declare function getCache<T = any>(key: string, value?: T): T;
export { hasCache, getCache, setCache };
