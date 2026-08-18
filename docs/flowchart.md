# SmartCache Flowchart

Logical decision flowchart for the SmartCache Cache Controller and Predictive Preloader.

```mermaid
flowchart TD
    Start([Client Request: GET /file?path=X]) --> CheckRAM{Is file X in RAM Cache?}
    
    CheckRAM -- Yes: HIT --> TouchEntry[Touch Entry: Update last_accessed & access_frequency]
    TouchEntry --> ReturnHIT[Return bytes + X-SmartCache-Status: HIT]
    
    CheckRAM -- No: MISS --> ReadDisk[Read binary bytes from Disk]
    ReadDisk --> PutRAM[Put into RAM Cache]
    PutRAM --> CheckCap{Is RAM Capacity Exceeded?}
    
    CheckCap -- Yes --> RunEviction[Run Eviction Engine: Select victim using LRU/LFU/Hybrid]
    RunEviction --> EvictFile[Evict Victim File from RAM]
    EvictFile --> ReturnMISS[Return bytes + X-SmartCache-Status: MISS]
    CheckCap -- No --> ReturnMISS
    
    ReturnHIT --> AsyncWorker[Trigger Async Task: Log Access & Update Markov Matrix]
    ReturnMISS --> AsyncWorker
    
    AsyncWorker --> CalcMarkov{Calculate P(Y|X) for all target Y. Is P >= 0.70?}
    CalcMarkov -- Yes --> InRAM{Is Y already in RAM?}
    InRAM -- No --> QueuePreload[Push Y to Background Preload Queue]
    QueuePreload --> PreloaderThread[Worker Thread 2: Read Y from Disk & Load into RAM]
    InRAM -- Yes --> End([End Request Flow])
    CalcMarkov -- No --> End
```
