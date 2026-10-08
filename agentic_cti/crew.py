import os
import yaml
from pathlib import Path
from typing import Dict, Any
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from tools.cachedb_tool import CacheDBInspectorTool
from tools.log_reader_tool import LogReaderTool
from tools.mitigation_tool import FirewallEnforcerTool, STIXExporterTool

@CrewBase
class ActifCTICrew:
    """Actif Agentic Cyber Threat Intelligence Crew Orchestration"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self):
        # Inisialisasi Tools
        self.cachedb_tool = CacheDBInspectorTool()
        self.log_reader_tool = LogReaderTool()
        self.firewall_tool = FirewallEnforcerTool()
        self.stix_tool = STIXExporterTool()

    @agent
    def l4_recon_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["l4_recon_specialist"],
            tools=[self.log_reader_tool, self.cachedb_tool],
            verbose=True,
        )

    @agent
    def dfir_file_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["dfir_file_specialist"],
            tools=[self.log_reader_tool, self.cachedb_tool],
            verbose=True,
        )

    @agent
    def attribution_hunter(self) -> Agent:
        return Agent(
            config=self.agents_config["attribution_hunter"],
            tools=[self.log_reader_tool, self.cachedb_tool],
            verbose=True,
        )

    @agent
    def threat_intel_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config["threat_intel_strategist"],
            tools=[self.cachedb_tool, self.log_reader_tool],
            verbose=True,
        )

    @agent
    def soc_incident_commander(self) -> Agent:
        return Agent(
            config=self.agents_config["soc_incident_commander"],
            tools=[self.firewall_tool, self.stix_tool, self.cachedb_tool],
            verbose=True,
        )

    @task
    def triage_recon_task(self) -> Task:
        return Task(
            config=self.tasks_config["triage_recon_task"],
        )

    @task
    def forensic_file_task(self) -> Task:
        return Task(
            config=self.tasks_config["forensic_file_task"],
        )

    @task
    def de_anonymize_hunter_task(self) -> Task:
        return Task(
            config=self.tasks_config["de_anonymize_hunter_task"],
        )

    @task
    def threat_modeling_task(self) -> Task:
        return Task(
            config=self.tasks_config["threat_modeling_task"],
        )

    @task
    def incident_response_action_task(self) -> Task:
        return Task(
            config=self.tasks_config["incident_response_action_task"],
            output_file="reports/latest_cti_incident_report.md",
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
