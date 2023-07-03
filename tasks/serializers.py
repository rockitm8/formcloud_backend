from rest_framework import serializers
from tasks.models import Preset, Task, Domain
import threading
import tasks.findContactForms as findContactForms
import tasks.sendContactForms as sendContactForms
from datetime import datetime


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'user', 'task_name', 'first_name', 'last_name', 'email', 'subject', 'phone_number',
                  'company', 'department', 'address', 'status', 'finished_date']

    def lineToBoolean(self, status, statusType):
        # check the text summary for a line about the statusType status and return it as a boolean
        # if doesnt exists return empty string

        if f"{statusType}: success" in status:
            return True
        elif f"{statusType}: fail" in status:
            return False
        else:
            return ""

    def statusToList(self, status):
        # creating a list of fields with each corresponding status
        return {
            "name": self.lineToBoolean(status, "Name"),
            "email": self.lineToBoolean(status, "Email"),
            "phone": self.lineToBoolean(status, "Phone"),
            "company": self.lineToBoolean(status, "Company"),
            "department": self.lineToBoolean(status, "Department"),
            "skype": self.lineToBoolean(status, "Skype"),
            "address": self.lineToBoolean(status, "Address"),
            "website": self.lineToBoolean(status, "Website"),
            "submit": self.lineToBoolean(status, "Submit"),
        }

    def autoFill(self, task, domain):
        fullName = task.first_name + task.last_name

        inputFields = {
            "name": fullName if fullName else "",
            "email": task.email if task.email else "",
            "phone": task.phone_number if task.phone_number else "",
            "subject": task.subject if task.subject else "",
            "message": "test",
            "company": task.company if task.company else "",
            "department": task.department if task.department else "",
            "skype": "",
            "address": task.address if task.address else "",
            "website": ""
        }
        status = sendContactForms.simpleRun(
            [domain["contact_page"]], inputFields)  # Outputs a text summary
        # Return a list of each field status based on the text summary
        statusList = self.statusToList(status)
        print(statusList)
        print(domain)
        Domain.objects.filter(task=task, domain_name=domain["domain_name"]).update(
            form_sent=False if statusList["submit"] == "" else statusList["submit"],
            went_over_manually=False,
            sent_manually=False)

    def runScript(self, task):
        domains = self.context['request'].data['domains']
        domain_list = []
        for domain in domains:
            domain_list.append(Domain.objects.create(
                task=task, domain_name=domain,
                status="Pending"))

        # result = findContactForms.Simple_Run(domains)

        for domain in domain_list:
            domain.status = "Running"
            domain.save()
            result = findContactForms.handleUrl(domain.domain_name)
            if (result is not None):
                hasForm = result["contact_page"] != ""
                hasContactPage = hasForm or len(result["no_form"]) > 0

                if hasForm:
                    contactPage = result["contact_page"]
                elif hasContactPage:
                    contactPage = result["no_form"][0]
                else:
                    contactPage = "None"
                Domain.objects.filter(pk=domain.id).update(
                    domain_name=result["domain_name"], reached_at=result["reached_at"],
                    status="Success", contact_page=contactPage,
                    emails_found=len(result["emails_found"]), contact_form=hasForm)
                # Domain.objects.filter() .create(
                #   task=task, domain_name=domain["domain_name"], reached_at= domain["reached_at"],
                #   status="Success", contact_page= contactPage,
                #   emails_found= len(domain["emails_found"]), contact_form= hasForm)

                scriptThread = threading.Thread(
                    target=self.autoFill, args=(task, result))
                scriptThread.start()
            else:
                Domain.objects.filter(pk=domain.id).update(status="Fail")

        Task.objects.filter(pk=task.id).update(
            status="Finished", finished_date=datetime.today())

    def create(self, validated_data):
        task = Task.objects.create(**validated_data)
        scriptThread = threading.Thread(target=self.runScript, args=(task,))
        scriptThread.start()
        return task

    # def runTaskAutomation(self, domain_ist, task):
    #   scriptThread = threading.Thread(target=self.runScript, args=(domain_ist,task,))
    #   scriptThread.start()

class PresetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preset
        fields = ['id', 'user', 'preset_name', 'first_name', 'last_name', 'email', 'subject', 'phone_number',
                  'company', 'department', 'address']

class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = ['task', 'domain_name', 'reached_at', 'status', 'contact_page', 'emails_found',
                  'contact_form', 'form_sent', 'went_over_manually', 'sent_manually']
