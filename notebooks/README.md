# Notebooks

The logic for each task lives in `src/` as tested, importable modules rather
than notebook cells, so it can be unit-tested and reused by the dashboard.
For submission, each notebook here should be a thin wrapper that imports
from `src/` and focuses on narrative + visualization:

- `01_data_exploration.ipynb` -- calls `data_loader.py`, prints schema
  validation, record-type/pillar/confidence summaries.
- `02_eda.ipynb` -- calls `eda.py`: temporal coverage heatmap, Access
  trajectory, gender gap, event overlays, the 5 key insights.
- `03_event_impact_modeling.ipynb` -- calls `event_impact.py`: association
  matrix, Telebirr/M-Pesa validation against observed data.
- `04_forecasting.ipynb` -- calls `forecasting.py`: scenario table, forecast
  charts with confidence bands, progress-to-target.

```python
import sys; sys.path.insert(0, "../src")
from data_loader import load_unified_data
from eda import key_insights, plot_access_trajectory
df = load_unified_data()
```
