import gemini_api
import sys
sys.stdout.reconfigure(encoding='utf-8')
print(gemini_api.get_daily_summary_report())