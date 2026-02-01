from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db import models
from app.schemas import rubric
from app.core.security import get_current_user

router = APIRouter()

# Default rubric templates - EXACTLY matching ME4611GradeRubrics.pdf structure
# NOTE: TT and TM rubrics have subsections totaling 60 points, but max_points is 40.
# The grading calculation applies scaling: (raw_score / 60) * 40 to normalize to 40 points.
DEFAULT_RUBRICS = {
    "TT": {
        "role": "TT",
        "name": "Table Topic",
        "max_points": 40,
        "criteria": {
            "section_presentation": {
                "name": "Presentation Quality",
                "section": True,
                "max_points": 20,
                "subsections": {
                    "first_last_impression": {
                        "name": "First/Last Impression",
                        "description": "Self-introduction, repeat question, wrap-up",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    },
                    "balanced_argument": {
                        "name": "Balanced Argument",
                        "description": "Argue different aspects of the topic",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    },
                    "followup_questions": {
                        "name": "Follow-up Questions",
                        "description": "Handling of questions from audience",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    },
                    "stature_vocal": {
                        "name": "Stature and Vocal Quality",
                        "description": "Eye contact, body movements, voice level, \"ums\"",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    }
                }
            },
            "section_feedback": {
                "name": "Feedback on YouTube",
                "section": True,
                "max_points": 20,
                "description": "Constructive comments including one positive aspect and one possible improvement. Average score will be credited at the end of the semester",
                "subsections": {
                    "feedback_for_others": {
                        "name": "Feedback for _________________",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    },
                    "self_assessment": {
                        "name": "Self-Assessment",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    }
                }
            }
        },
        "deductions": {
            "time_deviation": {
                "name": "Speaking time deviates from 2 min. limit",
                "description": "-5pt per 15 sec",
                "points": 5,
                "per_unit": True
            },
            "comments_late": {
                "name": "Comments posted late",
                "description": "-5pts / comment",
                "points": 5
            }
        }
    },
    "TM": {
        "role": "TM",
        "name": "Toastmaster",
        "max_points": 40,
        "criteria": {
            "section_moderation": {
                "name": "Moderation of the Speaking Session",
                "section": True,
                "max_points": 20,
                "subsections": {
                    "first_last_impression": {
                        "name": "First/Last Impression",
                        "description": "Self-introduction, wrap-up",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    },
                    "transitions": {
                        "name": "Transitions between Speakers",
                        "description": "Speaker/topic introductions",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    },
                    "timing_followup": {
                        "name": "Timing and Follow-up Questions",
                        "description": "Enforcing approx. 2min. of questions",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    },
                    "stature_vocal": {
                        "name": "Stature and Vocal Quality",
                        "description": "Eye contact, body movements, voice level, \"ums\"",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    }
                }
            },
            "section_feedback": {
                "name": "Feedback on YouTube",
                "section": True,
                "max_points": 20,
                "description": "Constructive comments including one positive aspect and one possible improvement. Average score will be credited at the end of the semester",
                "subsections": {
                    "feedback_for_others": {
                        "name": "Feedback for _________________",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    },
                    "self_assessment": {
                        "name": "Self-Assessment",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    }
                }
            }
        },
        "deductions": {
            "table_topics_approval": {
                "name": "Table Topics not approved 24 hours prior to class",
                "description": "-20pt penalty",
                "points": 20
            },
            "comments_late": {
                "name": "Comments posted late",
                "description": "-5pt / comments",
                "points": 5
            }
        }
    },
    "Camera": {
        "role": "Camera",
        "name": "Camera Assistant",
        "max_points": 40,
        "criteria": {
            "section_video_footage": {
                "name": "Video Footage",
                "section": True,
                "max_points": 40,
                "subsections": {
                    "video_recorded": {
                        "name": "Video is Recorded",
                        "description": "Footage is obtained for all speakers (incl. Toast Master)",
                        "max_points": 20,
                        "type": "scale",
                        "min": 0,
                        "max": 20,
                        "step": 2
                    },
                    "video_posted": {
                        "name": "Video is Posted on YouTube",
                        "description": "Clips show individual speakers",
                        "max_points": 20,
                        "type": "scale",
                        "min": 0,
                        "max": 20,
                        "step": 2
                    },
                    "video_shared": {
                        "name": "\"Private\" Video Clips are Shared",
                        "description": "Clips have correct setting and are shared with students and instructors",
                        "max_points": 20,
                        "type": "scale",
                        "min": 0,
                        "max": 20,
                        "step": 2
                    }
                }
            }
        },
        "deductions": {
            "clips_late": {
                "name": "Video clips posted after 24 hr deadline",
                "description": "-20pts per day",
                "points": 20,
                "per_unit": True
            },
            "data_not_erased": {
                "name": "Data not erased from SD card",
                "description": "-10pts",
                "points": 10
            },
            "sd_not_returned": {
                "name": "SD card is not returned for next class meeting",
                "description": "-30pts",
                "points": 30
            }
        }
    },
    "SMT": {
        "role": "SMT",
        "name": "Six Minute Talk - Thermodynamics Topic Presentations",
        "max_points": 240,
        "criteria": {
            "section_technical": {
                "name": "Technical Comprehension",
                "section": True,
                "max_points": 100,
                "subsections": {
                    "theoretical_background": {
                        "name": "Theoretical Background",
                        "description": "Relationship to Thermodynamics",
                        "max_points": 20,
                        "type": "scale",
                        "min": 0,
                        "max": 20,
                        "step": 2
                    },
                    "description_subject": {
                        "name": "Description of Subject",
                        "description": "Depends on topic",
                        "max_points": 20,
                        "type": "scale",
                        "min": 0,
                        "max": 20,
                        "step": 2
                    },
                    "important_equations": {
                        "name": "Important Equations",
                        "description": "Relevant equations",
                        "max_points": 20,
                        "type": "scale",
                        "min": 0,
                        "max": 20,
                        "step": 2
                    },
                    "discussion_relevance": {
                        "name": "Discussion of Relevance",
                        "description": "Practical applications",
                        "max_points": 20,
                        "type": "scale",
                        "min": 0,
                        "max": 20,
                        "step": 2
                    },
                    "knowledge_subject": {
                        "name": "Knowledge of Subject",
                        "description": "Preparedness of the Speaker",
                        "max_points": 20,
                        "type": "scale",
                        "min": 0,
                        "max": 20,
                        "step": 2
                    }
                }
            },
            "section_speaking": {
                "name": "Speaking Style",
                "section": True,
                "max_points": 40,
                "subsections": {
                    "personal_presence": {
                        "name": "Personal Presence",
                        "description": "Self-introduction, introduce topic, wrap-up; eye contact, body movements, voice level, \"ums\"",
                        "max_points": 20,
                        "type": "scale",
                        "min": 0,
                        "max": 20,
                        "step": 2
                    },
                    "professionalism": {
                        "name": "Professionalism",
                        "description": "Know material without memorization; handling of questions from audience",
                        "max_points": 20,
                        "type": "scale",
                        "min": 0,
                        "max": 20,
                        "step": 2
                    }
                }
            },
            "section_slides": {
                "name": "Quality of Slides",
                "section": True,
                "max_points": 40,
                "subsections": {
                    "layout_design": {
                        "name": "Layout and Design",
                        "description": "Layout/color choice, appropriate font size",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    },
                    "structure_organization": {
                        "name": "Structure and Organization",
                        "description": "Title page, introduction, discussion, conclusion",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    },
                    "graphics_tables": {
                        "name": "Quality of Graphics/Tables",
                        "description": "Information clearly visible, axes/labels used",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    },
                    "focused_content": {
                        "name": "Focused Content",
                        "description": "Key points are clearly made",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    }
                }
            },
            "section_appropriateness": {
                "name": "Appropriateness of Topic",
                "section": True,
                "max_points": 20,
                "subsections": {
                    "topic_suitable": {
                        "name": "Topic suitable for 6 min. talk?",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    },
                    "relevance_thermo": {
                        "name": "Relevance to Thermodynamics",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    }
                }
            },
            "section_feedback": {
                "name": "Feedback on YouTube",
                "section": True,
                "max_points": 40,
                "description": "Constructive comments including one positive aspect and one possible improvement. Average score will be credited at the end of the semester",
                "subsections": {
                    "feedback_1": {
                        "name": "Feedback for _________________",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    },
                    "feedback_2": {
                        "name": "Feedback for _________________",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    },
                    "feedback_3": {
                        "name": "Feedback for _________________",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    },
                    "self_assessment": {
                        "name": "Self-Assessment",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    }
                }
            }
        },
        "deductions": {
            "time_deviation": {
                "name": "Speaking time deviates from 6 min. limit",
                "description": "-5pts per 15 sec",
                "points": 5,
                "per_unit": True
            },
            "slides_late": {
                "name": "Slides posted less than 24 hrs in advance",
                "description": "-50 pts",
                "points": 50
            },
            "no_handout": {
                "name": "No printed slide handout provided to instructor",
                "description": "-20pts",
                "points": 20
            },
            "subject_not_approved": {
                "name": "Subject not approved one week in advance",
                "description": "-50 pts / day",
                "points": 50,
                "per_unit": True
            },
            "comments_late": {
                "name": "Comments posted late",
                "description": "-5pts / comment",
                "points": 5
            }
        }
    },
    "Lead": {
        "role": "Lead",
        "name": "Group Leader Presentation",
        "max_points": 200,
        "criteria": {
            "section_technical": {
                "name": "Technical Comprehension",
                "section": True,
                "max_points": 100,
                "subsections": {
                    "theoretical_background": {
                        "name": "Theoretical Background",
                        "description": "Relationship to Thermodynamics",
                        "max_points": 20,
                        "type": "scale",
                        "min": 0,
                        "max": 20,
                        "step": 2
                    },
                    "discussion_relevance": {
                        "name": "Discussion of Relevance",
                        "description": "Goals of experiment, practical applications",
                        "max_points": 20,
                        "type": "scale",
                        "min": 0,
                        "max": 20,
                        "step": 2
                    },
                    "description_experiment": {
                        "name": "Description of Experiment",
                        "description": "Apparatus, procedure, relevant data",
                        "max_points": 20,
                        "type": "scale",
                        "min": 0,
                        "max": 20,
                        "step": 2
                    },
                    "required_calculations": {
                        "name": "Outline of Required Calculations",
                        "description": "Relevant equations",
                        "max_points": 20,
                        "type": "scale",
                        "min": 0,
                        "max": 20,
                        "step": 2
                    },
                    "predictions_results": {
                        "name": "Predictions for exp. results",
                        "description": "Predict results based on data manual",
                        "max_points": 20,
                        "type": "scale",
                        "min": 0,
                        "max": 20,
                        "step": 2
                    }
                }
            },
            "section_speaking": {
                "name": "Speaking Style",
                "section": True,
                "max_points": 40,
                "subsections": {
                    "personal_presence": {
                        "name": "Personal Presence",
                        "description": "Self-introduction, introduce topic, wrap-up; eye contact, body movements, voice level, \"ums\"",
                        "max_points": 20,
                        "type": "scale",
                        "min": 0,
                        "max": 20,
                        "step": 2
                    },
                    "professionalism": {
                        "name": "Professionalism",
                        "description": "Know material without memorization; handling of questions from audience",
                        "max_points": 20,
                        "type": "scale",
                        "min": 0,
                        "max": 20,
                        "step": 2
                    }
                }
            },
            "section_slides": {
                "name": "Quality of Slides",
                "section": True,
                "max_points": 40,
                "subsections": {
                    "layout_design": {
                        "name": "Layout and Design",
                        "description": "Layout/color choice, appropriate font size",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    },
                    "structure_organization": {
                        "name": "Structure and Organization",
                        "description": "Title page, introduction, discussion, conclusion",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    },
                    "graphics_tables": {
                        "name": "Quality of Graphics/Tables",
                        "description": "Information clearly visible, axes/labels used",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    },
                    "focused_content": {
                        "name": "Focused Content",
                        "description": "Key points are clearly made",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    }
                }
            },
            "section_efficiency": {
                "name": "Efficiency of Experiment",
                "section": True,
                "max_points": 20,
                "subsections": {
                    "knowledge_experiment": {
                        "name": "Knowledge of Experiment",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    },
                    "experiment_efficient": {
                        "name": "Experiment Run Efficiently",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    }
                }
            },
            "section_feedback": {
                "name": "Feedback on YouTube",
                "section": True,
                "max_points": 40,
                "description": "Constructive comments including one positive aspect and one possible improvement. Average score will be credited at the end of the semester",
                "subsections": {
                    "techn_feedback": {
                        "name": "Techn. Feedback for _________",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    },
                    "feedback_1": {
                        "name": "Feedback for _________________",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    },
                    "feedback_2": {
                        "name": "Feedback for _________________",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    },
                    "self_assessment": {
                        "name": "Self-Assessment",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    }
                }
            }
        },
        "deductions": {
            "time_deviation": {
                "name": "Speaking time deviates from 6 min. limit",
                "description": "-5pts per 15 sec",
                "points": 5,
                "per_unit": True
            },
            "slides_late": {
                "name": "Slides posted less than 24 hrs in advance",
                "description": "-50 pts",
                "points": 50
            },
            "no_handout": {
                "name": "No printed slide handout provided to instructor",
                "description": "-20pts",
                "points": 20
            },
            "comments_late": {
                "name": "Comments posted late",
                "description": "-5pts / comment",
                "points": 5
            }
        }
    },
    "Reporter": {
        "role": "Reporter",
        "name": "Group Reporter Presentation",
        "max_points": 200,
        "criteria": {
            "section_technical": {
                "name": "Technical Comprehension",
                "section": True,
                "max_points": 100,
                "subsections": {
                    "synopsis_theory": {
                        "name": "Synopsis of Theory/Experiment",
                        "description": "Summary of background, apparatus and goals",
                        "max_points": 20,
                        "type": "scale",
                        "min": 0,
                        "max": 20,
                        "step": 2
                    },
                    "presentation_raw_data": {
                        "name": "Presentation of Raw Data",
                        "description": "Discuss data taken in experiments",
                        "max_points": 20,
                        "type": "scale",
                        "min": 0,
                        "max": 20,
                        "step": 2
                    },
                    "discussion_data_analysis": {
                        "name": "Discussion of Data Analysis",
                        "description": "Steps are shown in experiment manuals",
                        "max_points": 20,
                        "type": "scale",
                        "min": 0,
                        "max": 20,
                        "step": 2
                    },
                    "overall_quality_results": {
                        "name": "Overall Quality of Results",
                        "description": "Quality and completeness of results",
                        "max_points": 20,
                        "type": "scale",
                        "min": 0,
                        "max": 20,
                        "step": 2
                    },
                    "discussion_conclusions": {
                        "name": "Discussion and Conclusions",
                        "description": "Experimental outcomes and significance",
                        "max_points": 20,
                        "type": "scale",
                        "min": 0,
                        "max": 20,
                        "step": 2
                    }
                }
            },
            "section_speaking": {
                "name": "Speaking Style",
                "section": True,
                "max_points": 40,
                "subsections": {
                    "personal_presence": {
                        "name": "Personal Presence",
                        "description": "Self-introduction, introduce topic, wrap-up; eye contact, body movements, voice level, \"ums\"",
                        "max_points": 20,
                        "type": "scale",
                        "min": 0,
                        "max": 20,
                        "step": 2
                    },
                    "professionalism": {
                        "name": "Professionalism",
                        "description": "Know material without memorization; handling of questions from audience",
                        "max_points": 20,
                        "type": "scale",
                        "min": 0,
                        "max": 20,
                        "step": 2
                    }
                }
            },
            "section_slides": {
                "name": "Quality of Slides",
                "section": True,
                "max_points": 40,
                "subsections": {
                    "layout_design": {
                        "name": "Layout and Design",
                        "description": "Layout/color choice, appropriate font size",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    },
                    "structure_organization": {
                        "name": "Structure and Organization",
                        "description": "Title page, introduction, discussion, conclusion",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    },
                    "graphics_tables": {
                        "name": "Quality of Graphics/Tables",
                        "description": "Information clearly visible, axes/labels used",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    },
                    "focused_content": {
                        "name": "Focused Content",
                        "description": "Key points are clearly made",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    }
                }
            },
            "section_data_quality": {
                "name": "Quality of Data Posted Online",
                "section": True,
                "max_points": 20,
                "subsections": {
                    "completeness_data": {
                        "name": "Completeness of Data Set",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    },
                    "explanatory_comments": {
                        "name": "Explanatory Comments Included",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    }
                }
            },
            "section_feedback": {
                "name": "Feedback on YouTube",
                "section": True,
                "max_points": 40,
                "description": "Constructive comments including one positive aspect and one possible improvement. Average score will be credited at the end of the semester",
                "subsections": {
                    "techn_feedback": {
                        "name": "Techn. Feedback for _________",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    },
                    "feedback_1": {
                        "name": "Feedback for _________________",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    },
                    "feedback_2": {
                        "name": "Feedback for _________________",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    },
                    "self_assessment": {
                        "name": "Self-Assessment",
                        "max_points": 10,
                        "type": "scale",
                        "min": 0,
                        "max": 10,
                        "step": 1
                    }
                }
            }
        },
        "deductions": {
            "time_deviation": {
                "name": "Speaking time deviates from 6 min. limit",
                "description": "-5pts per 15 sec",
                "points": 5,
                "per_unit": True
            },
            "no_handout": {
                "name": "No printed slide handout provided to instructor",
                "description": "-20pts",
                "points": 20
            },
            "slides_late": {
                "name": "Slides posted less than 24 hrs in advance",
                "description": "-50 pts",
                "points": 50
            },
            "data_posted_late": {
                "name": "Data posted after 48 hr deadline",
                "description": "-50 pts / day",
                "points": 50,
                "per_unit": True
            },
            "slides_late_duplicate": {
                "name": "Slides posted less than 24 hrs in advance",
                "description": "-50 pts",
                "points": 50
            },
            "comments_late": {
                "name": "Comments posted late",
                "description": "-5pts / comment",
                "points": 5
            }
        }
    }
}

@router.get("/", response_model=List[rubric.RubricTemplate])
def get_all_rubrics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    rubrics = db.query(models.RubricTemplate).filter(
        models.RubricTemplate.is_active == True
    ).all()
    
    # If no rubrics exist, create default ones
    if not rubrics:
        for role, template_data in DEFAULT_RUBRICS.items():
            db_rubric = models.RubricTemplate(**template_data)
            db.add(db_rubric)
        db.commit()
        
        rubrics = db.query(models.RubricTemplate).filter(
            models.RubricTemplate.is_active == True
        ).all()
    
    return rubrics

@router.get("/{role}", response_model=rubric.RubricTemplate)
def get_rubric_by_role(
    role: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Try to get from database
    db_rubric = db.query(models.RubricTemplate).filter(
        models.RubricTemplate.role == role,
        models.RubricTemplate.is_active == True
    ).first()
    
    # If not found, create from default
    if not db_rubric and role in DEFAULT_RUBRICS:
        db_rubric = models.RubricTemplate(**DEFAULT_RUBRICS[role])
        db.add(db_rubric)
        db.commit()
        db.refresh(db_rubric)
    
    if not db_rubric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rubric template not found"
        )
    
    return db_rubric

@router.post("/", response_model=rubric.RubricTemplate)
def create_rubric(
    rubric_data: rubric.RubricTemplateCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check if rubric for this role already exists
    existing = db.query(models.RubricTemplate).filter(
        models.RubricTemplate.role == rubric_data.role,
        models.RubricTemplate.is_active == True
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rubric for this role already exists"
        )
    
    db_rubric = models.RubricTemplate(**rubric_data.model_dump())
    db.add(db_rubric)
    db.commit()
    db.refresh(db_rubric)
    
    return db_rubric

@router.post("/init-defaults")
def initialize_default_rubrics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Initialize all default rubrics"""
    created = []
    
    for role, template_data in DEFAULT_RUBRICS.items():
        existing = db.query(models.RubricTemplate).filter(
            models.RubricTemplate.role == role,
            models.RubricTemplate.is_active == True
        ).first()
        
        if not existing:
            db_rubric = models.RubricTemplate(**template_data)
            db.add(db_rubric)
            created.append(role)
    
    db.commit()
    
    return {"message": f"Initialized {len(created)} rubrics", "roles": created}

@router.delete("/reset")
def reset_all_rubrics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete all rubrics and reinitialize with defaults"""
    # Delete all existing rubrics
    db.query(models.RubricTemplate).delete()
    db.commit()
    
    # Reinitialize with new structure
    created = []
    for role, template_data in DEFAULT_RUBRICS.items():
        db_rubric = models.RubricTemplate(**template_data)
        db.add(db_rubric)
        created.append(role)
    
    db.commit()
    
    return {"message": f"Reset complete. Initialized {len(created)} rubrics", "roles": created}

