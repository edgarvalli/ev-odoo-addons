export interface User {
    id: number;
    login: string;
    name: string;
    email: string;
    phone: string;
    group_ids: number[];
    partner_id: number;
    complete_name?: string;
    tz?: string;
    active: Boolean;
    avatar_128?: string;
    avatar_256?: string;
    avatar_512?: string;
    avatar_1024?: string;
    avatar_1920?: string;
}