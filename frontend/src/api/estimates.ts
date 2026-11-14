import {request,post} from './client';import type {Estimate} from '../types/domain';
export const list=()=>request<Estimate[]>('/estimates');
export const create=(data:unknown)=>post<Estimate>('/estimates',data);
