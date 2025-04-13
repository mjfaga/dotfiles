import { Payload, Response, Status, Transport } from '@amplitude/analytics-types';
export declare class BaseTransport implements Transport {
    send(_serverUrl: string, _payload: Payload): Promise<Response | null>;
    buildResponse(responseJSON: Record<string, any>): Response | null;
    buildStatus(code: number): Status;
}
//# sourceMappingURL=base.d.ts.map