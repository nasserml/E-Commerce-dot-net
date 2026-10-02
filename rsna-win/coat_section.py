    import json as _j
    _coat_resgated_ok = _coat_g96_ok = _coat_d4_ok = _coat_rv1_ok = False
    _coat_receipt = _g96_receipt = _rv1_receipt = None
    g96_out = d4_out = rv1_out = None
    def _run_residual_reader():
        nonlocal _coat_resgated_ok, _coat_g96_ok, _coat_d4_ok, _coat_rv1_ok, _coat_receipt, _g96_receipt, _rv1_receipt, g96_out, d4_out, rv1_out
        rsna_phase('residual_coat', 'START')
        try:
            _run_required_child([_sy.executable, '-c', child], env,
                                _P('/kaggle/working/resgated_runtime.log'))
            _coat_receipt = _j.loads(_P('/kaggle/working/_coat_arm_receipt.json').read_text())
            if int(_coat_receipt.get('fallback_studies', 0) or 0):
                rsna_event('coat_resgated_fallback_studies', count=int(_coat_receipt['fallback_studies']), failures=list(_coat_receipt.get('failures', []))[:20])
            _coat_resgated_ok = True
        except Exception as _coat_exc:
            rsna_event('coat_resgated_child_failed', error=f'{type(_coat_exc).__name__}: {str(_coat_exc)[:1500]}')
            print(f'[coat-arm] residual CoAt child FAILED; continuing without it (flagged): {type(_coat_exc).__name__}', flush=True)
            _coat_resgated_ok = False
        rsna_phase('residual_coat', 'COMPLETE', ok=_coat_resgated_ok)
    def _run_global96_reader():
        nonlocal _coat_resgated_ok, _coat_g96_ok, _coat_d4_ok, _coat_rv1_ok, _coat_receipt, _g96_receipt, _rv1_receipt, g96_out, d4_out, rv1_out
        G96_MAN_SHA = '015f09030e76f86274cadae40777b3c3cf5c19f8c835d5ad88e15db41903779e'
        G96_TIMM_SHA = '888981753e65cbaacfc07494370138b1700a27b1f0af587f4f9b47bc024161d0'
        g96_out = _P('/kaggle/working/g96_input/_coat_g96.csv')
        g96_out.parent.mkdir(exist_ok=True)
        rsna_phase('global96_coat', 'START')
        try:
            g96_art = find('coatnet_global96_top3_manifest.json', G96_MAN_SHA).parent
            g96_timm = g96_art / 'timm-1.0.22-py3-none-any.whl'
            if sha(g96_timm) != G96_TIMM_SHA:
                raise RuntimeError('Global96 timm wheel changed')
            g96_env = _P('/kaggle/working/_g96_env')
            _sp.run(
                [_sy.executable, '-m', 'pip', 'install', '--no-deps', '--quiet',
                 '--target', str(g96_env), str(g96_timm)],
                check=True,
            )
            g96_child = (
                "import sys, json, os\n"
                f"sys.path.insert(0, {str(g96_env)!r})\n"
                f"sys.path.insert(0, {str(envd)!r})\n"
                f"sys.path.insert(0, {str(g96_art)!r})\n"
                "import cv2; assert cv2.__version__ == '4.12.0', cv2.__version__\n"
                "import timm; assert timm.__version__ == '1.0.22', timm.__version__\n"
                "import torch; assert torch.cuda.device_count() == 2\n"
                "import coatnet_global96_baseline_top3_inference as rt\n"
                "assert rt.base.cv2.__version__ == '4.12.0'\n"
                "assert rt.MAX_EVAL_WINDOWS == 94, rt.MAX_EVAL_WINDOWS\n"
                "from pathlib import Path\n"
                "r = rt.run_submission("
                "competition_root=Path(os.environ['RSNA_COMP_ROOT']) "
                "if os.environ.get('RSNA_COMP_ROOT') "
                "else rt.base.find_competition_root(),\n"
                f"    artifact_root=Path({str(g96_art)!r}), "
                f"output_path=Path({str(g96_out)!r}),\n"
                "    gpu_batch_studies=2, backbone_micro_images=8)\n"
                "assert r['status'] == rt.SUBMISSION_STATUS\n"
                "assert r['models'] == 3\n"
                "assert [i['epoch'] for i in r['checkpoints']] == [16, 23, 18]\n"
                "print('[coat-child] global96 fallback_studies', r['fallback_studies'], flush=True)\n"
                "Path('/kaggle/working/_coat_g96_receipt.json').write_text("
                "json.dumps(r, indent=2))\n"
            )
            g96_env_vars = dict(_o.environ)
            g96_env_vars['CUDNN_CONV_WSCAP_DBG'] = '1024'
            g96_env_vars['RSNA_COMP_ROOT'] = _KE_NS['find_test_root']()
            g96_env_vars['PYTHONPATH'] = f"{g96_env}:{envd}:{g96_art}:" + g96_env_vars.get('PYTHONPATH', '')
            _run_required_child([_sy.executable, '-c', g96_child], g96_env_vars,
                                _P('/kaggle/working/global96_runtime.log'))
            _g96_receipt = _j.loads(_P('/kaggle/working/_coat_g96_receipt.json').read_text())
            if int(_g96_receipt.get('fallback_studies', 0) or 0):
                rsna_event('coat_global96_fallback_studies', count=int(_g96_receipt['fallback_studies']))
            _coat_g96_ok = True
        except Exception as _g96_exc:
            rsna_event('coat_global96_child_failed', error=f'{type(_g96_exc).__name__}: {str(_g96_exc)[:1500]}')
            print(f'[coat-arm] Global96 CoAt child FAILED; continuing without it (flagged): {type(_g96_exc).__name__}', flush=True)
            _coat_g96_ok = False
        rsna_phase('global96_coat', 'COMPLETE', ok=_coat_g96_ok)
    def _run_d4_reader():
        nonlocal _coat_resgated_ok, _coat_g96_ok, _coat_d4_ok, _coat_rv1_ok, _coat_receipt, _g96_receipt, _rv1_receipt, g96_out, d4_out, rv1_out
        rsna_phase('d4', 'START')
        d4_out = _P('/kaggle/working/d4_input')/'d4.csv'
        try:
            d4_manifest = _asset_find_asset('coatnet_pairfilm_manifest.json',
                '7ada0605bca6b0530569c6454e988ace479606a3328ed591d090e5764fea661d')
            timm_whl = d4_manifest.parent/'timm-1.0.22-py3-none-any.whl'
            if sha(timm_whl) != '888981753e65cbaacfc07494370138b1700a27b1f0af587f4f9b47bc024161d0':
                raise RuntimeError('D4 timm wheel changed')
            d4_env = _P('/kaggle/working/_d4_env')
            _sp.run([_sy.executable,'-m','pip','install','--no-deps','--quiet',
                '--target',str(d4_env),str(timm_whl)],check=True)
            d4_dir = _P('/kaggle/working/d4_input')
            d4_dir.mkdir(exist_ok=True)
            _asset_run_d4(d4_manifest.parent,d4_env,_KE_NS['find_test_root'](),d4_out)
            _coat_d4_ok = True
        except Exception as _d4_exc:
            rsna_event('coat_d4_child_failed', error=f'{type(_d4_exc).__name__}: {str(_d4_exc)[:1500]}')
            print(f'[coat-arm] D4 CoAt child FAILED; continuing without it (flagged): {type(_d4_exc).__name__}', flush=True)
            _coat_d4_ok = False
        rsna_phase('d4', 'COMPLETE', ok=_coat_d4_ok)
    def _run_repairv1_reader():
        nonlocal _coat_resgated_ok, _coat_g96_ok, _coat_d4_ok, _coat_rv1_ok, _coat_receipt, _g96_receipt, _rv1_receipt, g96_out, d4_out, rv1_out
        RV1_MAN_SHA = '99288a9a42f36ba544d7b0ad2fe645e3b1fc9c507c23802c16ca0d2e5085f684'
        rv1_out = _P('/kaggle/working/_coat_repairv1.csv')
        rsna_phase('repairv1_coat', 'START')
        try:
            rv1_art = find('coatnet_repairv1_top3_manifest.json', RV1_MAN_SHA).parent
            rv1_child = (
                "import sys, json, os\n"
                f"sys.path.insert(0, {str(envd)!r})\n"
                f"sys.path.insert(0, {str(rv1_art)!r})\n"
                "import cv2; assert cv2.__version__ == '4.12.0', cv2.__version__\n"
                "import torch; assert torch.cuda.device_count() == 2\n"
                "import coatnet_repairv1_top3_inference as rt\n"
                "assert rt.base.cv2.__version__ == '4.12.0'\n"
                "from pathlib import Path\n"
                "r = rt.run_submission("
                "competition_root=Path(os.environ['RSNA_COMP_ROOT']) "
                "if os.environ.get('RSNA_COMP_ROOT') "
                "else rt.base.find_competition_root(),\n"
                f"    artifact_root=Path({str(rv1_art)!r}), "
                f"output_path=Path({str(rv1_out)!r}),\n"
                "    gpu_batch_studies=2, backbone_micro_images=8)\n"
                "assert r['status'] == rt.SUBMISSION_STATUS\n"
                "assert r['models'] == 3\n"
                "assert [i['epoch'] for i in r['checkpoints']] == [12, 7, 11]\n"
                "print('[coat-child] repairv1 fallback_studies', r.get('fallback_studies', 0), flush=True)\n"
                "Path('/kaggle/working/_coat_repairv1_receipt.json').write_text("
                "json.dumps(r, indent=2))\n"
            )
            rv1_env_vars = dict(_o.environ)
            rv1_env_vars['CUDNN_CONV_WSCAP_DBG'] = '1024'
            rv1_env_vars['RSNA_COMP_ROOT'] = _KE_NS['find_test_root']()
            rv1_env_vars['PYTHONPATH'] = f"{envd}:{rv1_art}:" + rv1_env_vars.get('PYTHONPATH', '')
            _run_required_child([_sy.executable, '-c', rv1_child], rv1_env_vars,
                                _P('/kaggle/working/repairv1_runtime.log'))
            _rv1_receipt = _j.loads(_P('/kaggle/working/_coat_repairv1_receipt.json').read_text())
            if int(_rv1_receipt.get('fallback_studies', 0) or 0):
                rsna_event('coat_repairv1_fallback_studies', count=int(_rv1_receipt['fallback_studies']))
            _coat_rv1_ok = True
        except Exception as _rv1_exc:
            rsna_event('coat_repairv1_child_failed', error=f'{type(_rv1_exc).__name__}: {str(_rv1_exc)[:1500]}')
            print(f'[coat-arm] Repair-v1 CoAt child FAILED; continuing without it (flagged): {type(_rv1_exc).__name__}', flush=True)
            _coat_rv1_ok = False
        rsna_phase('repairv1_coat', 'COMPLETE', ok=_coat_rv1_ok)

    _parallel_pairs = _o.environ.get(
        'RSNA_PARALLEL_COAT_READERS',
        '1' if len(_RSNA_TEST_IDS) <= 48 else '0',
    ) == '1'
    if _parallel_pairs:
        for _pair in ((_run_residual_reader, _run_d4_reader),
                      (_run_global96_reader, _run_repairv1_reader)):
            with _KeThreadPool(max_workers=2) as _pool:
                _jobs = [_pool.submit(_reader) for _reader in _pair]
                for _job in _jobs:
                    _job.result()
    else:
        for _reader in (_run_residual_reader, _run_global96_reader,
                        _run_d4_reader, _run_repairv1_reader):
            _reader()
    pub = _pd.read_csv(raptor, dtype={'StudyInstanceUID': str})
    pub = rsna_frame(pub,_RSNA_TEST_IDS,_KE_LAB,'public Raptor')
    lab = [c for c in pub.columns if c != 'StudyInstanceUID']
    import numpy as _np
    # Retain BTKD inner blend coefficients; input/new family scores are unvalidated.
    private_alpha = 0.4
    public_rank = pub[lab].rank(method='average', pct=True)
    _members = []
    if _coat_resgated_ok:
        try:
            ours = _pd.read_csv(out, dtype={'StudyInstanceUID': str})
            ours = rsna_frame(ours,_RSNA_TEST_IDS,_KE_LAB,'resgated CoAt')
            if list(ours.columns) != list(pub.columns):
                raise RuntimeError('coat arm column drift')
            ours = ours.set_index('StudyInstanceUID').reindex(pub.StudyInstanceUID.astype(str).tolist()).reset_index()
            if ours[lab].isna().any().any():
                raise RuntimeError('coat arm does not cover every study')
            rsna_save_predictions('coat_resgated_rank',_RSNA_TEST_IDS,ours[lab].to_numpy(),lab)
            _members.append(('resgated_top3', ours[lab].rank(method='average', pct=True)))
        except Exception as _exc:
            rsna_event('coat_resgated_output_rejected', error=f'{type(_exc).__name__}: {str(_exc)[:500]}')
    if _coat_g96_ok:
        try:
            g96 = _pd.read_csv(g96_out, dtype={'StudyInstanceUID': str})
            g96 = rsna_frame(g96,_RSNA_TEST_IDS,_KE_LAB,'Global96 CoAt')
            if list(g96.columns) != list(pub.columns):
                raise RuntimeError('global96 arm column drift')
            g96 = g96.set_index('StudyInstanceUID').reindex(pub.StudyInstanceUID.astype(str).tolist()).reset_index()
            if g96[lab].isna().any().any():
                raise RuntimeError('global96 arm does not cover every study')
            rsna_save_predictions('coat_global96_rank',_RSNA_TEST_IDS,g96[lab].to_numpy(),lab)
            _members.append(('global96_top3', g96[lab].rank(method='average', pct=True)))
        except Exception as _exc:
            rsna_event('coat_global96_output_rejected', error=f'{type(_exc).__name__}: {str(_exc)[:500]}')
    if _coat_d4_ok:
        try:
            d4 = _pd.read_csv(d4_out,dtype={'StudyInstanceUID':str})
            d4 = rsna_frame(d4,_RSNA_TEST_IDS,_KE_LAB,'D4 CoAt')
            rsna_save_predictions('coat_d4_rank',_RSNA_TEST_IDS,d4[lab].to_numpy(),lab)
            if d4.StudyInstanceUID.duplicated().any() or list(d4.columns)!=list(pub.columns):
                raise RuntimeError('D4 schema/UID drift')
            d4 = d4.set_index('StudyInstanceUID').reindex(pub.StudyInstanceUID.astype(str))
            if d4[lab].isna().any().any():
                raise RuntimeError('D4 missing predictions')
            _members.append(('d4_swa3', d4[lab].reset_index(drop=True).rank(method='average',pct=True)))
        except Exception as _exc:
            rsna_event('coat_d4_output_rejected', error=f'{type(_exc).__name__}: {str(_exc)[:500]}')
    if _coat_rv1_ok:
        try:
            rv1 = _pd.read_csv(rv1_out, dtype={'StudyInstanceUID': str})
            rv1 = rsna_frame(rv1,_RSNA_TEST_IDS,_KE_LAB,'Repair-v1 CoAt')
            if list(rv1.columns) != list(pub.columns):
                raise RuntimeError('repairv1 arm column drift')
            rv1 = rv1.set_index('StudyInstanceUID').reindex(pub.StudyInstanceUID.astype(str).tolist()).reset_index()
            if rv1[lab].isna().any().any():
                raise RuntimeError('repairv1 arm does not cover every study')
            rsna_save_predictions('coat_repairv1_rank',_RSNA_TEST_IDS,rv1[lab].to_numpy(),lab)
            _members.append(('repairv1_top3', rv1[lab].rank(method='average', pct=True)))
        except Exception as _exc:
            rsna_event('coat_repairv1_output_rejected', error=f'{type(_exc).__name__}: {str(_exc)[:500]}')
    if not _members:
        rsna_event('coat_family_unavailable', note='public Raptor kept as the CoAt/Raptor input (flagged)')
        print('[coat-arm] no CoAt family member available; public Raptor retained (flagged)', flush=True)
        return 0
    # Family reduction: rank of the members' PROBABILITY mean, not the mean of their ranks.
    # Each child already writes its probability_mean (or the raw per-checkpoint probabilities)
    # beside its rank CSV, in the submission's own label order.  If any member's probabilities
    # are unavailable, fall back to the previous rank mix rather than drop the member.
    _PROB_FILES = {
        'resgated_top3': _P('/kaggle/working/coat_resgated_ep10_top3_predictions.npz'),
        'global96_top3': _P('/kaggle/working/g96_input/coatnet_global96_top3_predictions.npz'),
        'd4_swa3': _P('/kaggle/working/d4_input/coatnet_d4_depthzone_swa3_predictions.npz'),
        'repairv1_top3': _P('/kaggle/working/coatnet_repairv1_top3_predictions.npz'),
    }

    def _coat_member_probability(name):
        with _np.load(_PROB_FILES[name], allow_pickle=False) as z:
            uids = [str(u) for u in z['study_uids'].astype(str)]
            if 'probability_mean' in z.files:
                prob = _np.asarray(z['probability_mean'], dtype=_np.float64)
            else:
                prob = _np.asarray(z['raw_probabilities'], dtype=_np.float64).mean(axis=0)
        if prob.shape != (len(uids), len(lab)):
            raise RuntimeError(f'{name} probability shape drift {prob.shape}')
        frame = _pd.DataFrame(prob, columns=lab, index=uids)
        frame = frame.reindex(pub.StudyInstanceUID.astype(str).tolist())
        values = frame.to_numpy(_np.float64)
        if frame.isna().any().any():
            raise RuntimeError(f'{name} probabilities do not cover every study')
        if not _np.isfinite(values).all() or (values < 0).any() or (values > 1).any():
            raise RuntimeError(f'{name} probabilities are not finite in [0,1]')
        return frame.reset_index(drop=True)

    _probs = {}
    for _name, _ in _members:
        try:
            _probs[_name] = _coat_member_probability(_name)
        except Exception as _exc:
            rsna_event('coat_member_probability_unavailable', member=_name,
                       error=f'{type(_exc).__name__}: {str(_exc)[:300]}')
    if len(_members) >= 2 and len(_probs) == len(_members):
        _mean = sum(_probs[_n] for _n, _ in _members) / float(len(_members))
        private_rank = _mean.rank(method='average', pct=True)
        _family_reduction = 'rank_of_member_probability_mean'
    elif len(_members) == 2:
        private_rank = _asset_half_rank_mix(*[_member for _, _member in _members])
        _family_reduction = 'rank_sum_fallback_probabilities_unavailable'
    elif len(_members) > 2:
        # N-member fallback: mean of member ranks (the 2-member pairwise helper is
        # alignment-checked for exactly two frames and must not be called here).
        private_rank = (sum(_member for _, _member in _members) / float(len(_members))).rank(
            method='average', pct=True)
        _family_reduction = 'mean_of_member_ranks_fallback_probabilities_unavailable'
    else:
        rsna_event('coat_family_partial', member=_members[0][0])
        private_rank = _members[0][1]
        _family_reduction = 'single_member_rank'
    print('[coat-arm] family reduction: ' + _family_reduction, flush=True)
    print('[coat-arm] CoAt family members: ' + ', '.join(m for m, _ in _members), flush=True)
    family = pub.copy()
    family[lab] = private_rank
    family.to_csv('/kaggle/working/_coat_family_rank.csv', index=False)
    hybrid = pub.copy()
    hybrid[lab] = (1.0 - private_alpha) * public_rank + private_alpha * private_rank
    if not _np.isfinite(hybrid[lab].to_numpy(_np.float64)).all():
        raise RuntimeError('CoAt/Raptor hybrid contains non-finite values')
    tmp = raptor.with_name('.raptor_coat_hybrid.csv')
    hybrid.to_csv(tmp, index=False)
    _o.replace(tmp, raptor)
    raptor.with_name('_coat_raptor_blend_receipt.json').write_text(_j.dumps({
        'contract': 'public_raptor_private_residual_coat_v32_no_inner_rerank_v1', 'inner_rerank': False, 'private_alpha': private_alpha,
        'within_coat': {m: 1.0 / len(_members) for m, _ in _members} if len(_members) >= 2 else {_members[0][0]: 1.0}, 'public_raptor_alpha': 1.0 - private_alpha,
        'study_count': len(pub), 'finding_specific_weights': False, 'members': [m for m, _ in _members], 'family_reduction': _family_reduction}, indent=2, sort_keys=True) + '\n')
    return len(pub)
