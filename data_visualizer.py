import os
import re
import json
import ast
from typing import List, Tuple
from collections import Counter

import matplotlib.pyplot as plt
import seaborn as sns
from models import JobDescription

sns.set_theme(style="whitegrid", palette="muted")


class JobDataVisualizer:
    def __init__(self, jobs: List[JobDescription]):
        self.jobs = jobs
        os.makedirs("visualizations", exist_ok=True)
        plt.style.use('Solarize_Light2')

    def _parse_skills_field(self, skills_field) -> List[str]:
        if not skills_field:
            return []
        if isinstance(skills_field, (list, tuple)):
            return [str(x).strip() for x in skills_field if str(x).strip()]
        s = str(skills_field).strip()
        try:
            parsed = json.loads(s)
            if isinstance(parsed, list):
                return [str(x).strip() for x in parsed if str(x).strip()]
        except Exception:
            pass
        try:
            parsed = ast.literal_eval(s)
            if isinstance(parsed, (list, tuple)):
                return [str(x).strip() for x in parsed if str(x).strip()]
        except Exception:
            pass
        return [p.strip() for p in re.split(r",|;|\|", s) if p.strip()]

    def _compute_skill_counts(self, skill_type: str) -> Tuple[Counter, int]:
        counter = Counter()
        total_jobs = len(self.jobs)
        for job in self.jobs:
            skills = self._parse_skills_field(getattr(job, skill_type, None))
            for sk in set(skills):
                counter[sk] += 1
        return counter, total_jobs

    def _plot_pie_chart(self, data_dict, title, filename):
        plt.figure(figsize=(10, 8))
        plt.pie(
            data_dict.values(),
            labels=data_dict.keys(),
            autopct='%1.1f%%',
            startangle=140,
            textprops={'fontsize': 10}
        )
        plt.title(title, fontsize=14)
        plt.tight_layout()
        plt.savefig(f"visualizations/{filename}.png", bbox_inches="tight")
        plt.close()

    def plot_work_mode_pie(self):
        mode_counter = Counter(job.work_mode for job in self.jobs if job.work_mode)
        total_jobs = len(self.jobs)
        if not mode_counter:
            print("No data for work_mode")
            return
        mode_percent = {k: (v / total_jobs) * 100 for k, v in mode_counter.items() if k.lower() != "other" and k.lower() != "інше"}
        self._plot_pie_chart(mode_percent, "Work Mode — % of Job Listings", "work_mode_pie")

    def plot_skills_bar(self, skill_type: str, top_n: int = 10):
        if skill_type not in {"soft_skills", "hard_skills"}:
            raise ValueError("skill_type must be 'soft_skills' or 'hard_skills'")
        counter, total_jobs = self._compute_skill_counts(skill_type)
        if total_jobs == 0 or not counter:
            print(f"No data for {skill_type}")
            return
        percent_map = {k: (v / total_jobs) * 100 for k, v in counter.items()}
        sorted_items = sorted(percent_map.items(), key=lambda x: x[1], reverse=True)[:top_n]
        sorted_items = [(s, p) for s, p in sorted_items if s.lower() != "other" and s.lower() != "інше"]
        skills = [x[0] for x in sorted_items]
        values = [x[1] for x in sorted_items]
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(skills, values, color='skyblue', edgecolor='black')
        plt.ylabel("Percentage of Job Listings (%)")
        plt.title(f"Most popular {skill_type.replace('_', ' ')}")
        plt.ylim(0, 100)
        plt.xticks(rotation=45, ha='right')
        for bar, val in zip(bars, values):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f"{val:.1f}%", ha='center', fontsize=9)
        plt.tight_layout()
        out_path = f"visualizations/{skill_type}_bar.png"
        plt.savefig(out_path, bbox_inches="tight", dpi=150)
        plt.close()
        print(f"Saved: {out_path}")
