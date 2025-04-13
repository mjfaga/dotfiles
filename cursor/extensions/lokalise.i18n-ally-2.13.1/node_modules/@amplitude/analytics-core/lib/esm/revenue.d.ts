import { RevenueEventProperties, Revenue as IRevenue, ValidPropertyType } from '@amplitude/analytics-types';
export declare class Revenue implements IRevenue {
    private productId;
    private quantity;
    private price;
    private revenueType?;
    private properties?;
    private revenue?;
    constructor();
    setProductId(productId: string): this;
    setQuantity(quantity: number): this;
    setPrice(price: number): this;
    setRevenueType(revenueType: string): this;
    setRevenue(revenue: number): this;
    setEventProperties(properties: {
        [key: string]: ValidPropertyType;
    }): this;
    getEventProperties(): RevenueEventProperties;
}
//# sourceMappingURL=revenue.d.ts.map