---
title: "STISim: An open-source agent-based simulation framework for sexually transmitted infection transmission and vaccination strategies"

tags:
  - Python
  - agent-based model
  - sexually transmitted disease modeling
  - chlamydia
  - vaccination
  - sexual network
authors:
  - name: Qi Deng
    affiliation: 1,2
  - name: Grégoire Ranson
    affiliation: 2,3
  - name: Nicola Luigi Bragazzi 
    affiliation: 2,4,5
  - name: Valerie Bosch Castells
    affiliation: 6
  - name: Sandra S.Chaves
    affiliation: 6
  - name: Edward Thommes
    affiliation: 7,8
  - name: Jianhong Wu
    affiliation: 1,2
affiliations:
  - name: Centre of Excellence in Artificial Intelligence for Public Health Advancement, York University, Toronto, Canada
    index: 1
  - name: Laboratory for Industrial and Applied Mathematics, York University, Toronto, Canada
    index: 2
  - name: Institut Camille Jordan, Université Claude Bernard Lyon 1, Villeurbanne, France. 
    index: 3
  - name: Department of Food and Drugs, University of Parma, Parma, Italy
    index: 4
  - name: Department of Clinical Pharmacy, Saarland University, Saarbrücken, Germany
    index: 5
  - name: Sanofi, Lyon, France
    index: 6
  - name: Department of Mathematics & Statistics, University of Guelph, Guelph, Canada
    index: 7
  - name: formerly Sanofi, Toronto, Canada
    index: 8
  
  

date: 2026-07-04
bibliography: paper.bib
---

# Summary

STISim is a Python agent-based modeling framework for simulating sexually transmitted infection (STI) transmission and intervention strategies in heterogeneous sexual contact networks. The framework provides a modular representation of demographic processes, sexual partnership dynamics, infection transmission, screening, treatment, and vaccination. The current implementation is parameterized for Chlamydia trachomatis and includes disease-specific processes such as reinfection and pelvic inflammatory disease (PID), but the software architecture is designed to support adaptation to other STIs through modification of pathogen-specific parameters and disease progression modules.

The package is designed for scenario-based public health modeling. It supports experiments that vary vaccine coverage, vaccine efficacy, target population, vaccine duration, time-varying protection, and scale-up schedules. Simulation outputs are stored as tabular time series for downstream analysis of infection states, vaccination status, partner counts, recurrent episodes, and long-term infection outcomes.

# Statement of need

Many STI control questions require models that represent individual heterogeneity, sexual partnership networks, screening programs, treatment pathways, reinfection, and intervention uptake. While several general epidemiological modeling frameworks exist, adapting them to STI-specific transmission processes often requires substantial customization. STISim was developed to provide a reusable agent-based framework for modeling STI transmission and intervention strategies while retaining flexibility for disease-specific extensions.

The current implementation focuses on Chlamydia trachomatis and has been applied to evaluate vaccination strategies in a peer-reviewed simulation study [@deng_chlamydia_vaccine_study]. However, the underlying framework is structured so that transmission parameters, disease progression pathways, intervention mechanisms, and health outcomes can be modified to represent other STIs.

# State of the field

A variety of software tools are available for infectious disease modeling, ranging from compartmental modeling platforms to agent-based and network-based simulation frameworks. Agent-based models are widely used to represent heterogeneous individuals and emergent system-level behavior [@bonabeau2002agent], and standardized description protocols have been proposed to improve transparency and reproducibility of individual-based and agent-based models [@grimm2006standard]. Examples of general epidemiological software include EpiModel, which provides flexible network modeling capabilities for infectious disease transmission [@jenness2018epimodel], Covasim, an agent-based framework developed for evaluating intervention strategies during the COVID-19 pandemic [@kerr2021covasim], HPVsim, an open-source, multi-scale agent-based Python package designed to model multi-genotype HPV transmission and interventions to support global cervical cancer elimination strategies [@stuart2024hpvsim]. These tools offer powerful general-purpose infrastructures for epidemiological simulation but often require substantial customization to represent the behavioral, partnership, and intervention processes that are central to STIs.

STIs present unique modeling challenges because transmission occurs through dynamic sexual partnership networks and is influenced by heterogeneous sexual behavior, screening practices, treatment seeking, partner notification, and vaccination uptake. Empirical and theoretical work on sexual networks has shown that partnership distributions and network structure are important determinants of STI transmission and prevention strategy design [@liljeros2001web; @kretzschmar2000sexual]. Chlamydia-specific individual-based and sexual-network models have been used to evaluate screening, partner notification, and treatment strategies [@azizi2020agent; @qu2020screening]. However, many published STI models are developed for individual studies and are not released as reusable software, limiting transparency, reproducibility, and adaptation to new research questions.

STISim addresses this gap by providing an open-source agent-based framework specifically designed for STI transmission modeling. The framework combines demographic processes, sexual partnership dynamics, infection transmission, screening, treatment, and vaccination within a modular simulation architecture. The current implementation is parameterized for *Chlamydia trachomatis* and includes disease-specific outcomes such as PID. However, the software separates core simulation components from pathogen-specific processes, allowing researchers to adapt the framework to other STIs by modifying transmission parameters, disease progression pathways, intervention mechanisms, and health outcomes while reusing the underlying simulation engine and network structure.

# Software design

The model is organized around five main modules to separate individual state, network dynamics, simulation orchestration, and scenario definition. `agent.py` defines the `Agent` object and handles infection initialization, PID development, weekly disease-state updates, vaccination status, and demographic aging and replacement. `relationship.py` forms and dissolves partnerships, assigns partnership durations, and applies transmission probabilities within active relationships. `simulation.py` advances the weekly simulation loop and records agent-level time series. `simulation_setup.py` constructs experiment parameter combinations and dispatches simulations in parallel. `vaccine_scenarios.py` defines vaccination strategies and maintains coverage targets after vaccine introduction.

This separation allows users to modify intervention assumptions or disease-specific natural history without rewriting the core simulation loop. Model parameters are stored separately in `config.json`, allowing users to adjust population size, time horizon, age distributions, transmission probabilities, screening rates, treatment rates, relationship durations, and vaccine assumptions without modifying source code. The repository includes a minimal from-scratch example for installation checks and a saved-initialization workflow for larger calibrated simulations.

The framework separates disease-independent processes (agent demographics, partnership dynamics, simulation scheduling, and intervention delivery) from disease-specific processes (transmission probabilities, natural history, clinical outcomes, and intervention effects). This design is consistent with recommendations for transparent agent-based model specification [@grimm2006standard] and allows users to adapt the framework to alternative STI pathogens while reusing the core simulation engine and network structure. The saved-initialization pathway supports reproducible large-scale experiments, while the minimal example provides a lightweight verification route for reviewers and new users.

# Research impact statement

STISim supports reproducible simulation experiments for evaluating STI intervention strategies in heterogeneous populations. The software underlies a peer-reviewed study of chlamydia vaccination strategies in the United States [@deng_chlamydia_vaccine_study], demonstrating its use in policy-relevant vaccine impact analysis. That study used the model to evaluate infection and downstream health outcomes under alternative vaccine assumptions.

Although the current release focuses on *Chlamydia trachomatis*, the framework is intended to support future applications to other sexually transmitted infections through modification of pathogen-specific modules and parameters. By releasing the software as an open-source package with tests, example workflows, citation metadata, and contribution guidelines, STISim provides a transparent and extensible platform for STI transmission modeling, vaccination policy analysis, and public health decision support.

# AI usage disclosure

The authors used OpenAI Codex to assist with copy-editing documentation, checking repository readiness, and drafting portions of the software paper text. The authors reviewed, edited, and validated all AI-assisted outputs and made the scientific, software design, and authorship decisions.

# Acknowledgements

This research was funded by the NSERC-Sanofi Industrial Research Chair Program in Vaccine Mathematics, Modelling, and Manufacturing (517504), and by the NSERC-Mitacs Alliance Program in Advanced Mathematical Technologies for Respiratory Infection Risk Assessment and Pharmaceutical Intervention Scenario Analysis (481502654). The funders had no role in the design, decision to publish, or preparation of the manuscript or the package STISim.

# References
