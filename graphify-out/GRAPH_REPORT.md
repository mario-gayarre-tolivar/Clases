# Graph Report - Clases  (2026-11-16)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1453 nodes · 4651 edges · 61 communities (50 shown, 11 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 682 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `353270bc`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13
- Community 14
- Community 15
- Community 16
- Community 17
- Community 18
- Community 19
- Community 20
- Community 21
- Community 22
- Community 23
- Community 24
- Community 25
- Community 26
- Community 27
- Community 28
- Community 29
- Community 30
- Community 31
- Community 32
- Community 33
- Community 34
- Community 35
- Community 36
- Community 37
- Community 38
- Community 39
- Community 40
- Community 42
- Community 43
- Community 44
- Community 45
- Community 46
- Community 47
- Community 48
- Community 49
- Community 50
- Community 51
- Community 52
- Community 59

## God Nodes (most connected - your core abstractions)
1. `Student` - 72 edges
2. `TutoringSession` - 65 edges
3. `AcademicCatalogSnapshot` - 53 edges
4. `Subject` - 49 edges
5. `create_app()` - 49 edges
6. `ExerciseType` - 47 edges
7. `Topic` - 47 edges
8. `AttemptOutcome` - 41 edges
9. `ExerciseAttempt` - 41 edges
10. `ErrorCause` - 39 edges

## Surprising Connections (you probably didn't know these)
- `InMemoryCatalogRepository` --uses--> `ExerciseType`  [INFERRED]
  backend/src/tutoring/application/fakes.py → backend/src/tutoring/domain/entities/catalog.py
- `ManageCatalogUseCase` --uses--> `ExerciseType`  [INFERRED]
  backend/src/tutoring/application/use_cases/manage_catalog.py → backend/src/tutoring/domain/entities/catalog.py
- `CatalogRepository` --uses--> `ExerciseType`  [INFERRED]
  backend/src/tutoring/domain/ports/repositories.py → backend/src/tutoring/domain/entities/catalog.py
- `test_sklearn_analyzer_fallback_when_untrained()` --uses--> `ExerciseType`  [INFERRED]
  backend/tests/integration/test_sklearn_analyzer.py → backend/src/tutoring/domain/entities/catalog.py
- `test_sklearn_analyzer_trained_inference()` --uses--> `ExerciseType`  [INFERRED]
  backend/tests/integration/test_sklearn_analyzer.py → backend/src/tutoring/domain/entities/catalog.py

## Import Cycles
- None detected.

## Communities (61 total, 11 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.08
Nodes (71): applySavedSessionMeta(), buildSveltePropValuesFromLiveElement(), checkpointPayload(), clampVariantIndex(), closedClipPath(), completeParameterGenerationIfReady(), completeParameterPublication(), completeSourceInjection() (+63 more)

### Community 1 - "Community 1"
Cohesion: 0.08
Nodes (15): ExerciseType, _index_catalog_items(), Subject, Topic, SqliteCatalogRepository, test_sqlite_catalog_persistence_and_snapshot(), test_sqlite_session_persistence_lifecycle(), test_catalog_entities_normalize_and_validate_names() (+7 more)

### Community 2 - "Community 2"
Cohesion: 0.07
Nodes (18): FeatureExtractor, FeatureVector, _compute_exam_urgency_bonus(), _evaluate_readiness_risk(), collect_timed_attempts(), compute_dominant_error_cause(), compute_failure_delta(), compute_learning_trend() (+10 more)

### Community 3 - "Community 3"
Cohesion: 0.09
Nodes (53): ae(), be(), bt(), Ce(), Ct(), de(), dt(), _e() (+45 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (8): ValidationError, require_non_empty(), ExamGoal, test_require_non_empty_strips_valid_text(), test_exam_goal_rejects_blank_title_and_negative_horizon(), test_exam_goal_validates_title_and_computes_days_remaining(), test_student_add_exam_goal_validates_past_date_and_duplicates(), test_student_upcoming_exams_filters_and_sorts_chronologically()

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (18): AttemptOutcome, ErrorCause, LearningTrend, InvalidAttemptError, ExerciseAttempt, ExamAlert, SubjectPriority, WeakExerciseType (+10 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (55): actionLabel(), applyConfigureBarChrome(), bindConfigureCountPillTooltip(), bindConfigureInlineControlHover(), bindConfigureModifierPillHover(), buildConfigureActionControl(), buildConfigureCountControl(), buildConfigureRow() (+47 more)

### Community 7 - "Community 7"
Cohesion: 0.11
Nodes (50): applyLiveBarPreference(), beginNewLiveConfiguration(), cancelEditing(), cancelEditingToPicking(), cancelInsertConfigure(), clearAnnotations(), clearInsertPicking(), closeTunePopover() (+42 more)

### Community 8 - "Community 8"
Cohesion: 0.09
Nodes (8): ExerciseAttemptDTO, SessionDTO, StudentDiagnosticDTO, GenerateStudentDiagnosticUseCase, RecordSessionUseCase, CatalogRepository, SessionRepository, StudentRepository

### Community 9 - "Community 9"
Cohesion: 0.10
Nodes (21): ApiError, HttpTutoringApi, CatalogTreeSubject, CatalogTreeTopic, CreateExamGoalPayload, CreateExerciseTypePayload, CreateStudentPayload, CreateSubjectPayload (+13 more)

### Community 10 - "Community 10"
Cohesion: 0.06
Nodes (42): addManualContextText(), applyEditing(), buildLocatorForLeaf(), canRestoreManualEditElement(), collectEditableTextRows(), visit(), collectManualContextPieces(), walk() (+34 more)

### Community 11 - "Community 11"
Cohesion: 0.07
Nodes (41): buildCollapsible(), buildColorModels(), buildDesignHeader(), buildListHtml(), buildRadiiModels(), buildTypographyModels(), copyToClipboard(), cssSafe() (+33 more)

### Community 12 - "Community 12"
Cohesion: 0.10
Nodes (6): InMemorySessionRepository, TutoringSession, _validate_duration(), SqliteSessionRepository, test_in_memory_session_repository(), test_session_normalizes_notes_and_exposes_immutable_attempts()

### Community 13 - "Community 13"
Cohesion: 0.12
Nodes (12): HeuristicPedagogicalAnalyzer, AcademicCatalogSnapshot, Student, test_analyzer_identifies_weak_exercise_types_excluding_mastered_ones(), test_analyzer_propagates_subject_and_overall_trends_with_regression_bonus(), test_analyzer_rejects_invalid_hyperparameters(), test_analyzer_subject_weighted_failure_rate_reflects_recency(), test_analyzer_with_no_sessions_returns_insufficient_data_and_empty_scores() (+4 more)

### Community 14 - "Community 14"
Cohesion: 0.09
Nodes (37): agentHasWorkInFlight(), agentStatusText(), barPaletteForTheme(), brandMarkSvg(), buildParamsPanel(), buildSteerQueueHint(), designPanelCss(), detectPageTheme() (+29 more)

### Community 15 - "Community 15"
Cohesion: 0.11
Nodes (33): abortSvelteComponentInjection(), buildInsertPlaceholderSnapshotFromDom(), buildPickedAnchorSnapshot(), captureAndEmit(), cleanup(), cleanupAcceptedSession(), clearHandled(), clearMountErrorCard() (+25 more)

### Community 16 - "Community 16"
Cohesion: 0.08
Nodes (27): applyGlobalBarLabelState(), applyParamDefaults(), applyParamValue(), applySavedParamValues(), buildPlaceholderResizeHandles(), clearSteerAwaitTimer(), cursorForPlaceholderEdge(), globalBarModeToggles() (+19 more)

### Community 17 - "Community 17"
Cohesion: 0.10
Nodes (6): _NamedEntity, PedagogicalAnalyzerPort, StudentDiagnostic, SklearnPedagogicalAnalyzer, test_sklearn_analyzer_fallback_when_untrained(), test_sklearn_analyzer_trained_inference()

### Community 18 - "Community 18"
Cohesion: 0.09
Nodes (29): devDependencies, eslint@^9.9.0, @eslint/js@^9.9.0, eslint-plugin-react-hooks@^5.1.0-rc.0, eslint-plugin-react-refresh@^0.4.9, globals@^15.9.0, jsdom@^25.0.0, @testing-library/jest-dom@^6.5.0 (+21 more)

### Community 19 - "Community 19"
Cohesion: 0.10
Nodes (30): abandonForeignSession(), abandonSupersededGo(), applyOriginalAttrsToSvelteAnchor(), commitAcceptedSvelteComponentToDom(), componentModuleCandidates(), describeMountFailure(), detectDevServerBase(), discardOrphanedSession() (+22 more)

### Community 20 - "Community 20"
Cohesion: 0.21
Nodes (14): CatalogTreeDTO, CatalogTreeSubjectDTO, CatalogTreeTopicDTO, CreateExerciseTypeDTO, CreateSubjectDTO, CreateTopicDTO, ExerciseTypeDTO, SubjectDTO (+6 more)

### Community 21 - "Community 21"
Cohesion: 0.16
Nodes (28): armPageChatForTyping(), attachSteerFocusDebug(), attachSteerFocusGuard(), clearSteerFocusRecoverTimer(), collapsePageChat(), expandPageChat(), focusConfigureInput(), focusPageChatInput() (+20 more)

### Community 22 - "Community 22"
Cohesion: 0.17
Nodes (27): clearStoredManualApplyState(), fetchPendingCount(), handleManualEditActivity(), hidePendingApplyDock(), manualApplyLoadingText(), manualApplyStateKey(), manualEditEventForCurrentPage(), numberOrNull() (+19 more)

### Community 23 - "Community 23"
Cohesion: 0.12
Nodes (12): TutoringApi, ActiveSection, App(), AppProps, CatalogTree, StudentSummary, CatalogPage(), CatalogPageProps (+4 more)

### Community 24 - "Community 24"
Cohesion: 0.18
Nodes (9): ExerciseAttemptInputDTO, RecordSessionDTO, InMemoryCatalogRepository, InMemoryStudentRepository, record_session(), test_in_memory_catalog_repository(), test_in_memory_student_repository(), test_generate_student_diagnostic_orchestration() (+1 more)

### Community 25 - "Community 25"
Cohesion: 0.11
Nodes (9): DomainError, init_sqlite_db(), CreateExamGoalPayload, CreateExerciseTypePayload, CreateStudentPayload, CreateSubjectPayload, CreateTopicPayload, ExerciseAttemptPayload (+1 more)

### Community 26 - "Community 26"
Cohesion: 0.12
Nodes (22): absolutizeUrls(), averageRgb01(), bufferToBase64(), captureChromeNodes(), captureElementFromRenderedAncestor(), captureElementToBlob(), collectFontCssText(), collectFontFaces() (+14 more)

### Community 27 - "Community 27"
Cohesion: 0.23
Nodes (9): CreateExamGoalDTO, CreateStudentDTO, ExamGoalDTO, StudentDetailDTO, StudentSummaryDTO, ManageStudentsUseCase, EntityNotFoundError, test_add_exam_goal_validates_student_and_subject_existence() (+1 more)

### Community 28 - "Community 28"
Cohesion: 0.09
Nodes (9): create_app(), add_exam_goal(), create_exercise_type(), create_student(), create_subject(), create_topic(), test_catalog_api_flow_and_error_handling(), test_session_and_diagnostic_api_endpoints() (+1 more)

### Community 29 - "Community 29"
Cohesion: 0.19
Nodes (15): formatDaysRemaining(), riskBadgeClass(), StudentDiagnosticPanel(), StudentDiagnosticPanelProps, trendBadgeClass(), ERROR_CAUSE_LABELS, formatPercent(), OUTCOME_LABELS (+7 more)

### Community 30 - "Community 30"
Cohesion: 0.16
Nodes (15): createLiveBrowserDomHelpers(), activeElementDeep(), cloneWithoutChrome(), copyTextViaSelection(), cssId(), liveUiRoot(), makeFrozenAnchor(), raiseHitModal() (+7 more)

### Community 31 - "Community 31"
Cohesion: 0.19
Nodes (17): createLiveBrowserSessionState(), clearHandled(), clearScrollY(), clearSession(), isHandled(), loadSession(), markHandled(), nextCheckpointRevision() (+9 more)

### Community 32 - "Community 32"
Cohesion: 0.16
Nodes (18): buildSvelteExpressionTextMap(), buildSveltePropValuesV2(), cloneWithoutElements(), collectTextNodes(), collectVisibleTexts(), cssEscapeIdent(), elementMatchesOriginalMarkup(), escapeRegExp() (+10 more)

### Community 33 - "Community 33"
Cohesion: 0.11
Nodes (17): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+9 more)

### Community 34 - "Community 34"
Cohesion: 0.29
Nodes (17): actOnAgentTarget(), agentTargetBusyReason(), agentTargetOverlayGone(), agentTargetTaken(), claimAgentTarget(), claimAndActOnAgentTarget(), declineAgentTargetBusy(), declineAgentTargetUnresolvable() (+9 more)

### Community 35 - "Community 35"
Cohesion: 0.20
Nodes (17): beginEditPin(), buildAnnotationsForCapture(), buildPinElement(), cancelEditingPin(), clampPlaceholderSize(), finalizeEditingPin(), initAnnotOverlay(), localCoords() (+9 more)

### Community 36 - "Community 36"
Cohesion: 0.20
Nodes (16): configureVoiceContext(), finishVoiceSession(), isEmbeddedPreviewBrowser(), releaseVoiceEngine(), sendSteerCheckpoint(), startVoice(), steerSpeechRecognitionCtor(), steerVoiceContext() (+8 more)

### Community 37 - "Community 37"
Cohesion: 0.13
Nodes (12): dependencies, react@^18.3.1, react-dom@^18.3.1, scripts, build, dev, lint, preview (+4 more)

### Community 38 - "Community 38"
Cohesion: 0.23
Nodes (14): acceptedDomAlreadyClean(), clearHandledWrapperReloadStamp(), commitAcceptedVariantToDom(), deferredRecoverySuperseded(), ensureAcceptedDomClean(), findAcceptedRuntimeWrappers(), handledWrapperReloadKey(), reloadAfterMissingAcceptedDom() (+6 more)

### Community 39 - "Community 39"
Cohesion: 0.19
Nodes (7): @testing-library/react@^16.0.1, @testing-library/user-event@^14.5.2, vitest@^2.0.5, sampleCatalog, @testing-library/react, @testing-library/user-event, vitest

### Community 40 - "Community 40"
Cohesion: 0.19
Nodes (7): AttemptOutcome, ErrorCause, DraftAttempt, ERROR_CAUSES, formatLocalDateTimeInput(), OUTCOMES, RecordSessionPage()

### Community 42 - "Community 42"
Cohesion: 0.18
Nodes (11): applyPlaceholderSizingStyles(), createInsertPlaceholder(), detectInsertAxis(), detectInsertAxisFromStyle(), ensureInsertLine(), handleMouseMove(), hideHighlightTagTooltip(), placeholderSizing() (+3 more)

### Community 45 - "Community 45"
Cohesion: 0.31
Nodes (9): bindEditBadgeProxy(), editBadgeProxyTargets(), initEditBadge(), initEditBadgeHitProxies(), proxyMouseEvent(), setImportantStyle(), styleEditBadgeProxy(), syncEditBadgeHitProxies() (+1 more)

### Community 46 - "Community 46"
Cohesion: 0.52
Nodes (6): globToRegex(), matchesScope(), normalizeIgnoreRule(), normalizeIgnoreValue(), pageCandidates(), resolveDetectIgnores()

### Community 47 - "Community 47"
Cohesion: 0.33
Nodes (6): computeInsertPosition(), groupSiblingRows(), hitSiblingInsertGap(), horizontalOverlap(), insertLineCoords(), resolveInsertHover()

### Community 48 - "Community 48"
Cohesion: 0.40
Nodes (6): documentRefClassSuffix(), documentRefIdSuffix(), documentRefSegment(), elementMatchesManualRefSegment(), indexAmongSameTag(), normalizeDocumentRefToken()

### Community 49 - "Community 49"
Cohesion: 0.33
Nodes (6): findMatchingCssBrace(), prefixCssSelectors(), scopeCssBlock(), shouldScopeNestedCssAtRule(), splitCssSelectorList(), unwrapSvelteGlobalSelector()

### Community 50 - "Community 50"
Cohesion: 0.40
Nodes (4): interface, default_prompt, display_name, short_description

### Community 51 - "Community 51"
Cohesion: 0.50
Nodes (4): applyPlaceholderDimensions(), materializePlaceholderWidth(), placeholderWidthIsImplicit(), startPlaceholderEdgeResize()

### Community 52 - "Community 52"
Cohesion: 0.50
Nodes (3): compileShader(), showShaderBitmapFallback(), showShaderOverlay()

## Knowledge Gaps
- **1 isolated node(s):** `tutoring-app`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 267 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Student` connect `Community 13` to `Community 1`, `Community 2`, `Community 4`, `Community 8`, `Community 43`, `Community 12`, `Community 17`, `Community 20`, `Community 24`, `Community 27`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `Student` (e.g. with `InMemoryStudentRepository` and `ManageStudentsUseCase`) actually correct?**
  _`Student` has 30 INFERRED edges - model-reasoned connections that need verification._
- **What connects `tutoring-app` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.07766599597585513 - nodes in this community are weakly interconnected._
- **Why does `create_app()` connect `Community 28` to `Community 1`, `Community 4`, `Community 8`, `Community 43`, `Community 12`, `Community 13`, `Community 44`, `Community 20`, `Community 24`, `Community 25`, `Community 27`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Are the 23 inferred relationships involving `TutoringSession` (e.g. with `InMemorySessionRepository` and `RecordSessionUseCase`) actually correct?**
  _`TutoringSession` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.07596153846153846 - nodes in this community are weakly interconnected._