import logging
from typing import Union

from hubgrep_indexer.constants import HOST_TYPE_GITHUB, HOST_TYPE_GITEA, HOST_TYPE_GITLAB
from hubgrep_indexer.lib.state_manager.abstract_state_manager import AbstractStateManager, Block

logger = logging.getLogger(__name__)


class IStateHelper:
    # maximum consecutive returned callbacks containing no results, before we blind-reset
    # only relevant for non-paginated results when overriding IStateHelper.has_reached_end (github)
    empty_results_max = 100

    @classmethod
    def resolve_state(cls, hosting_service_id: str,
                      state_manager: AbstractStateManager,
                      block_uid: str,
                      parsed_repos: list) -> Union[bool, None]:
        """
        Default implementation for resolving if we have consumed all
        repositories available, and its time to start over.

        This assumes that we give out blocks based on pagination,
        and reaching the end of pagination means we reset the
        state and start over.

        Returns state_manager.get_run_is_finished() OR None
        - true/false if we reached end, None if block is unrelated to the current run
        """
        block = state_manager.get_block(
            hoster_prefix=hosting_service_id, block_uid=block_uid)

        if not block:
            # Block has already been deleted from the previous run, no state changes
            logger.info(f"block no longer exists - no state changes, uid: {block_uid}")
            return None
        else:
            is_run_finished = state_manager.get_is_run_finished(
                hoster_prefix=hosting_service_id)
            if is_run_finished:
                logger.info(f"skipping state update for outdated block, uid: {block_uid}")
                # this Block belongs to an old run, so we avoid touching any state for it
                return None

        state_manager.finish_block(
            hoster_prefix=hosting_service_id, block_uid=block_uid)
        if len(parsed_repos) == 0:
            state_manager.increment_empty_results_counter(
                hoster_prefix=hosting_service_id, amount=1)
        else:
            state_manager.set_empty_results_counter(
                hoster_prefix=hosting_service_id, count=0)

        # check on the effects of the block transaction
        has_reached_end = cls.has_reached_end(
            hosting_service_id=hosting_service_id,
            state_manager=state_manager,
            parsed_repos=parsed_repos,
            block=block)
        has_too_many_empty = cls.has_too_many_consecutive_empty_results(
            hosting_service_id=hosting_service_id,
            state_manager=state_manager)

        if has_reached_end:
            logger.info(f'crawler reached end for hoster: {hosting_service_id}')
            state_manager.finish_run(hoster_prefix=hosting_service_id)
        elif has_too_many_empty:
            logger.info(f'crawler reach max empty results for hoster: {hosting_service_id}')
            state_manager.finish_run(hoster_prefix=hosting_service_id)
        else:
            # we are somewhere in the middle of a hosters repos
            # and we count up our confirmed ids and continue
            if isinstance(block.ids, list) and len(block.ids) > 0:
                repo_id = block.ids[-1]
            else:
                repo_id = block.to_id
            state_manager.set_highest_confirmed_block_repo_id(
                hoster_prefix=hosting_service_id, repo_id=repo_id)

        # finally return and terminate the while loop
        return state_manager.get_is_run_finished(hosting_service_id)

    @classmethod
    def has_too_many_consecutive_empty_results(cls,
                                               hosting_service_id: str,
                                               state_manager: AbstractStateManager) -> bool:
        has_too_many_empty_results = state_manager.get_empty_results_counter(
            hoster_prefix=hosting_service_id) >= cls.empty_results_max
        return has_too_many_empty_results

    @classmethod
    def has_reached_end(cls,
                        hosting_service_id: str,
                        state_manager: AbstractStateManager,
                        block: Block,
                        parsed_repos: list) -> bool:
        """
        Try to find out if we reached the end of repos on this hoster.

        This should only be the case, if we have an empty result set
        on the last handed-out block.

        This method assumes that results are coming from a paginated source,
        such that reaching 0 results means there are no more pages. We also
        give a little bit of extra leeway by allowing partial results before
        we reach our conclusion that it's the end of pagination.
        """
        # we dont reason about partially filled results, only check/assume end of run if we reached 0 results
        if len(parsed_repos) > 0:
            return False

        # get the ending repo id from a block we have seen containing results
        highest_confirmed_id = state_manager.get_highest_confirmed_block_repo_id(
            hoster_prefix=hosting_service_id)

        # get ending repo id of the block after the last confirmed one
        last_block_id = highest_confirmed_id + state_manager.batch_size

        # check if our current empty block comes after a block with confirmed results
        return block.to_id == last_block_id


class GitHubStateHelper(IStateHelper):
    @classmethod
    def has_reached_end(cls,
                        hosting_service_id: str,
                        state_manager: AbstractStateManager,
                        block: Block,
                        parsed_repos: list) -> bool:
        """
        We default to False for GitHub as we receive lots of gaps within results.
        Maybe a whole block contains private
        repos and we get nothing back - therefore we cannot assume that we have
        reached the end when a block is empty.

        We instead rely on "IStateHelper.has_too_many_consecutive_empty_results(...)"
        to resolve and reset GitHub.
        """
        return False


class GiteaStateHelper(IStateHelper):
    pass


class GitLabStateHelper(IStateHelper):
    pass


def get_state_helper(hosting_service_type):
    state_helpers = {
        HOST_TYPE_GITHUB: GitHubStateHelper,
        HOST_TYPE_GITEA: GiteaStateHelper,
        HOST_TYPE_GITLAB: GitLabStateHelper
    }
    return state_helpers[hosting_service_type]()
