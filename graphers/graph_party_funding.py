# -*- coding: utf-8 -*-
import logging
from utils import mongo
from data_models import models


class GraphPartyFunding():
    def __init__(self):
        self._logger = logging.getLogger('')

    def run(self):
        self.data_models = models
        self.cache = mongo.MongoInterface()
        self.cache_data = self.cache.db.parsed_party_funding

        self.all_mps = list(self.cache_data.find())
        for doc in self.all_mps:
            name = doc["recipient"]
            donor = doc["donor_name"]
            self._logger.debug("\n..................")
            self._logger.debug("recipient: %s" % name)
            # self._logger.debug(doc)
            recipient = self._get_recipient(name, doc)
            category = self._create_category(name, donor)
            donor = self._get_donor(donor, doc)
            donation = self._create_donation(doc)
            recipient.link_funding_category(category)
            category.link_donor(donor)
            category.link_funding(donation)
            self._logger.debug("..................")

    def _get_recipient(self, name, entry):
        props = {
            "recipient_type": entry["recipient_type"],
            "donee_type": entry["donee_type"]
        }
        new_recipient = self.data_models.DonationRecipient(name)
        if not new_recipient.exists:
            self._logger.debug("*not found*")
            new_recipient.create()
        new_recipient.update_recipient(props)
        return new_recipient

    def _create_category(self, name, donor):
        props = {"recipient": name, "donor": donor}
        category_name = u"{} and {}".format(donor, name)
        new_category = self.data_models.FundingRelationship(category_name)
        if not new_category.exists:
            new_category.create()
        new_category.update_category_details(props)
        return new_category

    def _get_donor(self, name, entry):
        props = {
            "donor_type": entry["donor_type"],
            "company_reg": entry["company_reg"]
        }
        new_donor = self.data_models.Donor(name)
        if not new_donor.exists:
            new_donor.create()
        new_donor.update_donor(props)
        return new_donor

    def _create_donation(self, entry):
        if len(entry["received_date"]) > 0:
            received_date = entry["received_date"]
        else:
            received_date = "Missing Received Date"
        props = {
            "recipient": entry["recipient"],
            "donor_name": entry["donor_name"],
            "amount": self.convert_to_number(entry["value"]),
            "ec_reference": entry["ec_reference"],
            "nature": entry["nature_provision"],
            "purpose": entry["purpose"],
            "recd_by": entry["recd_by"],
            "received_date": entry["received_date"],
            "reported_date": entry["reported_date"],
            "accepted_date": entry["accepted_date"],
            "6212": entry["6212"]
        }
        summary = u"{} - {} - {} - {}".format(
            entry["recipient"],
            entry["donor_name"],
            received_date,
            entry["value"]
        )
        self._logger.debug(summary)
        new_donation = self.data_models.RegisteredFunding(summary)
        new_donation.create()
        new_donation.update_funding_details(props)
        new_donation.set_dates(
            entry["received_date"],
            entry["reported_date"],
            entry["accepted_date"]
        )
        return new_donation

    @staticmethod
    def convert_to_number(amount):
        amount = amount.replace(u"£", u"")
        if ",00" == amount[-3:]:
            amount = amount.replace(",00", "")
        if "," in amount:
            amount = amount.replace(",", "")
        if "." in amount:
            amount = amount.split(".")[0]
        if amount.isdigit():
            return int(amount)
        else:
            return 0
