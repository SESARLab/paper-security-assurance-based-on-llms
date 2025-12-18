# Integrazione di Large Language Models per il supporto decisionale nella Security Assurance

## Tesi triennale - 2024/25

Repo allegata al lavoro di tesi svolto presso il SEcure Service-oriented Architecture Research Lab (SESARlab). 

La repo è organizzata come segue: 

- **Benchmarking**
    - Alcune utility sviluppate per effettuare valutazioni secondo le metriche definite. 
    - Dataset generati, tra cui `2-60-m-m-s`, utilizzato nella sezione "Preferenze" LLM-as-a-judge dell'elaborato. 
- **Confgen**
    - Liste di controlli framework standard
    - Frontend PoC DSS
    - Utility per convertire excel2json, utilizzato per convertire standard in formato per modello
- **Forecast**
    - Esperimenti per generatori di time-series e forecasters che utilizzano approcci differenti
- **Models**
    - Software da eseguire su VM con GPU per l'esecuzione di modelli ed API per interazione
    - Tester in locale di modelli e utility per conversione formato conversazioni
- **Preferences**
    - Risultati preferenze riportati nella tesi, suddivisi per modello giudice
    - Utility poi non utilizzata per preparare batch per OpenAPI
    - Script per automatizzare il processo di valutazione 
- **Prompts**
    - Prompt proposti per i vari task, incluso LLM-as-a-judge. Utilizzati per gli esempi ufficiali dell'elaborato. 

Ulteriori informazioni nei singoli README.md

```
.
├── benchmarking
│   ├── benchmark.py
│   ├── datasets
│   ├── results
├── confgen
│   ├── control_lists
│   └── gen_server
├── forecast
│   ├── data 
│   ├── forecasters
│   └── generators
├── models
│   ├── misc
│   └── server
├── preferences
│   ├── data
│   ├── old
│   └── src
├── prompts
└── README.md
```