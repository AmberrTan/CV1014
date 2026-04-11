# Unused Code Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove unused files, models, and fields to simplify the codebase.

**Architecture:** This is a scoped cleanup. We delete an unused module and remove unused model classes/fields, ensuring references are gone. No runtime behavior changes are intended.

**Tech Stack:** Python, FastAPI, Pydantic

---

## File Structure
- Delete: `/Users/zhoufuwang/Projects/cv1014_2/src/osm_quality.py`
- Modify: `/Users/zhoufuwang/Projects/cv1014_2/src/models.py`
- Re-scan: `rg` for remaining references

### Task 1: Remove Unused Module

**Files:**
- Delete: `/Users/zhoufuwang/Projects/cv1014_2/src/osm_quality.py`

- [ ] **Step 1: Delete the unused module**

```bash
git rm /Users/zhoufuwang/Projects/cv1014_2/src/osm_quality.py
```

- [ ] **Step 2: Verify no references remain**

Run:
```bash
rg -n "osm_quality" /Users/zhoufuwang/Projects/cv1014_2/src /Users/zhoufuwang/Projects/cv1014_2/tests /Users/zhoufuwang/Projects/cv1014_2/docs /Users/zhoufuwang/Projects/cv1014_2/README.md
```
Expected: no matches.

- [ ] **Step 3: Commit**

```bash
git add -u

git commit -m "Remove unused osm quality module"
```

### Task 2: Remove Unused Models and Fields

**Files:**
- Modify: `/Users/zhoufuwang/Projects/cv1014_2/src/models.py`

- [ ] **Step 1: Update models**

```python
from pydantic import BaseModel
from typing import List, Optional, Tuple
from enum import Enum

class FitnessGoal(str, Enum):
    muscle_gain = "muscle_gain"
    weight_loss = "weight_loss"
    general_fitness = "general_fitness"
    powerlifting = "powerlifting"
    cardio = "cardio"

class UserLocationProfile(BaseModel):
    user_id: str
    address_text: Optional[str] = None
    preferred_location: Tuple[float, float]

class UserProfile(BaseModel):
    user_id: str
    age_group: Optional[str] = None
    gender: Optional[str] = None
    budget_range: Tuple[float, float]
    preferred_location: Tuple[float, float] # (lat, lon)
    fitness_goals: List[FitnessGoal]
    access_24h: bool = False
    requires_classes: bool = False
    requires_shower_lockers: bool = False
    female_friendly: bool = False
    sport_filters: List[str] = []
    equipment_filters: List[str] = []
    max_travel_distance_km: float

class Gym(BaseModel):
    gym_id: str
    name: str
    location: Tuple[float, float] # (lat, lon)
    price: float
    facilities: List[str]
    sports: List[str] = []
    equipment: List[str] = []
    rating: float
    popularity_score: float
    tags: List[str]

class ScoreExplanation(BaseModel):
    distance: float
    budget: float
    facilities: float
    rating: float

class Recommendation(BaseModel):
    gym_id: str
    name: str
    distance_km: float
    score: float
    explanation: ScoreExplanation
```

- [ ] **Step 2: Re-scan for dangling references**

Run:
```bash
rg -n "UserQuery|RecommendationResponse|prefers_less_crowded|Field" /Users/zhoufuwang/Projects/cv1014_2/src /Users/zhoufuwang/Projects/cv1014_2/tests /Users/zhoufuwang/Projects/cv1014_2/docs /Users/zhoufuwang/Projects/cv1014_2/README.md
```
Expected: no matches.

- [ ] **Step 3: Commit**

```bash
git add /Users/zhoufuwang/Projects/cv1014_2/src/models.py

git commit -m "Remove unused models and fields"
```

