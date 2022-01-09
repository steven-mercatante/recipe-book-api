from django.contrib.auth.models import AbstractUser
from django.db.models import Q

from recipes.models import ShareConfig


class User(AbstractUser):
    def get_shared_user_ids(self):
        """
        Returns set of user_ids that are sharing (either as granter or grantee)
        Recipes with current user.
        Set excludes current user ID.
        """
        # list of tuples: [(granter_id, grantee_id), (granter_id, grantee_id), ...]
        user_ids = ShareConfig.objects.filter(
            Q(granter=self) | Q(grantee=self)
        ).values_list('granter_id', 'grantee_id')

        return {
            user_id
            for sub_list in list(user_ids)
            for user_id in sub_list
            if user_id != self.id
        }
