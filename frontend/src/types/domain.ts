export interface User{email:string;role:string}
export interface Column{code:string;label:string;unit:string}
export interface Alternative{alternative_id:string;name:string;values:Record<string,number>}
export interface Dataset{id:string;name:string;source:string;columns:Column[];alternatives:Alternative[];created_at:string}
export interface Criterion{code:string;direction:'cost'|'benefit'}
export interface Criteria{id:string;name:string;dataset_id:string;criteria:Criterion[];created_at:string}
export interface Judgment{id:string;name:string;criteria_set_id:string;matrix:number[][];cr_threshold:number;perturbation:number;created_at:string}
export interface Ranking extends Alternative{score:number|null;rank:number|null;d_plus:number|null;d_minus:number|null;min_rank:number|null;max_rank:number|null}
export interface CriterionMeta extends Column{direction:'cost'|'benefit'}
export interface Result{ahp:{weights:number[];lambda_max:number;ci:number;ri:number;cr:number;threshold:number;cr_warning:boolean;iterations:number;eigen_residual:number;ri_table:Record<string,number>;rule:string};matrix_original:number[][];criteria:CriterionMeta[];topsis:{available:boolean;reason:string;issues:{criterion_index:number;reason:string}[];norms:number[];scores:(number|null)[];ranks:(number|null)[];d_plus:(number|null)[];d_minus:(number|null)[];ideal_best:number[];ideal_worst:number[]};alternatives:Ranking[];perturbation:number;simulation?:Simulation;sensitivity:{criterion_index:number;multiplier:number;weights:number[];scores:(number|null)[];ranks:(number|null)[]}[];checksum:string;assumptions:string[]}
export interface Triple{min:number;mode:number;max:number}
export interface EstimateRange{alternative_id:string;values:Record<string,Triple>}
export interface Estimate{id:string;name:string;dataset_id:string;ranges:EstimateRange[];created_at:string}
export interface SimulationRow{alternative_id:string;name:string;exclusive_first:number;tied_first:number;not_first:number;unrankable:number;counted_samples:number;exclusive_first_share:number|null;tied_first_share:number|null;not_first_share:number|null;unrankable_share:number|null}
export interface SimulationBasis{estimate_id:string;estimate_name:string;ranges:EstimateRange[];weights:number[];directions:string[];seed:number;requested_samples:number;completed_samples:number;distribution:string;stream_key:string;weights_rule:string;degenerate_rule:string;count_rule:string;version:string;checksum:string}
export interface Simulation{version:string;estimate_id:string;estimate_name:string;distribution:string;stream_key:string;degenerate_rule:string;count_rule:string;weights:number[];weights_rule:string;requested_samples:number;completed_samples:number;seed:number;status:'completed'|'partial';timed_out:boolean;timeout_seconds:number|null;elapsed_seconds:number;unavailable_samples:number;unavailable_reasons:Record<string,number>;alternatives:SimulationRow[];basis:SimulationBasis;basis_checksum:string;note:string}
export interface Run{id:string;judgment_id:string;status:string;result:Result;error:string;estimate_id:string;samples:number;seed:number;created_at:string}
export interface Review{id:string;run_id:string;note:string;decision:string;accept_warning:boolean;author:string;created_at:string}
export interface Report{id:string;run_id:string;title:string;published_by:string;basis:Partial<SimulationBasis>;created_at:string}
export interface Audit{id:string;actor:string;action:string;status:number;created_at:string}
