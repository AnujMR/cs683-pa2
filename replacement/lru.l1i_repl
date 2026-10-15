#include "cache.h"

// initialize replacement state
void CACHE::l1i_initialize_replacement()
{
	cout << NAME << " has LRU replacement policy" << endl;
}

// find replacement victim
uint32_t CACHE::l1i_find_victim(uint32_t cpu, uint64_t instr_id, uint32_t set, const BLOCK *current_set, uint64_t ip, uint64_t full_addr, uint32_t type)
{
    // baseline LRU
    return lru_victim(cpu, instr_id, set, current_set, ip, full_addr, type); 
}

// called on every cache hit and cache fill
void CACHE::l1i_update_replacement_state(uint32_t cpu, uint32_t set, uint32_t way, uint64_t full_addr, uint64_t ip, uint64_t victim_addr, uint32_t type, uint8_t hit, uint8_t isInstruction)
{
        string TYPE_NAME;
    if (type == LOAD)
        TYPE_NAME = "LOAD";
    else if (type == RFO)
        TYPE_NAME = "RFO";
    else if (type == PREFETCH)
        TYPE_NAME = "PF";
    else if (type == WRITEBACK)
        TYPE_NAME = "WB";
    else if (type == LOAD_TRANSLATION)
	TYPE_NAME = "L_TN";
    else if (type == PREFETCH_TRANSLATION)
	TYPE_NAME = "P_TN";
    else if (type == TRANSLATION_FROM_L1D)
	TYPE_NAME = "TN_L1D";
    else
        assert(0);

    if (hit)
        TYPE_NAME += "_HIT";
    else
        TYPE_NAME += "_MISS";
        
    if ((type == WRITEBACK) && ip)
        assert(0);

    // uncomment this line to see the LLC accesses
    // cout << "CPU: " << cpu << "  LLC " << setw(9) << TYPE_NAME << " set: " << setw(5) << set << " way: " << setw(2) << way;
    // cout << hex << " paddr: " << setw(12) << full_addr << " ip: " << setw(8) << ip << " victim_addr: " << victim_addr << dec << endl;

    // baseline LRU
    if (hit && (type == WRITEBACK)) // writeback hit does not update LRU state
        return;

    return lru_update(set, way);
}

void CACHE::l1i_replacement_final_stats()
{

}
