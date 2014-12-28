#!/usr/bin/env python2

from lxml import etree
import sys
import re
import httplib2
from apiclient.discovery import build
from oauth2client import client
from oauth2client.file import Storage
from oauth2client.tools import run
import json
import webbrowser


REMOVE_ATTRS = ['id', 'htmlLink', 'iCalUID', 'gadget', 'attendees']

def output_rpt_line():
    print '\n\n{0}\n{0}\n\n'.format('='*78)

class GCalMover(object):
    """A class for moving/deduplifying google calendar events."""

    def __init__(self, credentials):
        self.credentials = credentials
        self.get_gcal_service()

    def get_gcal_service(self):
        """Get a google calendar api service."""
        http = httplib2.Http()
        http = self.credentials.authorize(http)
        self.service = build('calendar', 'v3', http=http)
        self.gcal_events = self.service.events()

    def get_calendars(self):
        """Get a list of the users' google calendars."""
        calendars = []
        page_token = None
        while True:
            s = self.service
            calendar_list = s.calendarList().list(pageToken=page_token).execute()
            for i in calendar_list['items']:
                cal = s.calendarList().get(calendarId=i['id']).execute()
                calendars.append(cal)
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break
        self.calendars = calendars
        return calendars

    def process_calendar_dups(self, 
                              source_calendars,
                              destination_calendar,
                              replace_text=[],
                              dry_run=False,
                              html=True,
                              std_out=False):
        """Deduplify one or more google calendars.

        First, the events of one or more source calendars are scanned and 
        placed into groups of similar events.  Groups with more than one 
        event are considered to be duplicates.  

        Then the duplicate groups are tested to weed out false positives and
        sorted in an attempt to keep the "correct" event, and to removing 
        any unique data.

        Then the duplicate events are moved to another calendar.  No events
        are ever deleted.  To completely delete events, select a new/blank
        destination calendar and then use the website to delete the 
        destination calendar after completion. 
        """
        # replace_text example (VEA): [(r'\\n',''), (r'\\',''), (r'\n','')]
        self.source_calendars = source_calendars
        self.destination_calendar = destination_calendar
        self.destination_calendar_id = destination_calendar.get('id')
        self.replace_text = replace_text
        self.events = {}
        self.log = []
        for source_calendar in source_calendars:
            self.find_dup_groups(source_calendar.get('id'))
        for group in self.events.values():
            if len(group) > 1:
                self.process_group(group, 
                                   self.destination_calendar_id, 
                                   dry_run=dry_run, 
                                   html=html, 
                                   std_out=std_out)
        from pudb import set_trace; set_trace()
        self.log = '\n'.join(self.log)
        return self.log

    def find_dup_groups(self, source_calendar_id):
        """Scan a source calendar and place the events into groups.

        The groups are comprised of events with identical sets of attributes
        (start, end, recurrence, summary, description, location).  Groups
        containing more than one event are considered to be duplicated
        events, which are then subjected to further tests.  
        """
        page_token = None
        while True:
            page = self.gcal_events.list(calendarId=source_calendar_id,
                                         pageToken=page_token).execute()
            items = page.get('items')
            if items:
                for i in items:
                    try:
                        start = tuple(i.get('start').values())
                    except:
                        continue
                    try:
                        end = tuple(i.get('end').values())
                    except:
                        continue

                    try:
                        recurrence = tuple(i.get('recurrence'))
                    except:
                        recurrence = None


                    summary = self.get_key_text('summary', i)
                    if not summary:
                        continue
                    
                    description = self.get_key_text('description', i)
                    location = self.get_key_text('location', i)

                    # build a tuple from 5 attributes with which we test 
                    # uniqueness
                    item_key = (start, end, recurrence, summary, 
                                description, location)
                    
                    # the idea here is that the item_key is a boiled-down version
                    # of the event, which will match exactly among duplicated 
                    # events, even when attributes like the itemId differ.

                    # and because we store the boiled-down attrs as tuples, 
                    # the item_key can be used as a dict key, the value of which 
                    # is a list of all the matching (full) items which share that 
                    # key.

                    # get the list of matching items which have this same item_key,
                    # or if this is the first time this key has been seen, add the
                    # new key to the events dict and add the current event as the 
                    # first item in the list/value.

                    item_vals = self.events.setdefault(item_key, [])
                    item_vals.append(i)

            # get the next page of events
            page_token = page.get('nextPageToken')
            if not page_token:
                break

    def get_key_text(self, attr, event):
        kt = event.get(attr)
        if kt:
            kt = kt.strip()
            for rt in self.replace_text:
                kt = re.sub(rt[0], rt[1], kt)
        return kt

    def process_group(self, group, destination_calendar_id, dry_run=False, html=True, std_out=False):
        """Sort groups, then move duplicate events to destination calendar."""
        group = self.sort_group(group)
        tests_passed, tests_msg = self.run_group_tests(group)
        results = {'keep': group[0],
                   'tests': tests_msg,
                   'remove': []}
        for i in group[1:]:
            r = {'event': i,
                 'moved_result': None}
            if not dry_run and tests_passed:
                moved = self.move_event(i, destination_calendar_id)
                r['moved_result'] = moved
            results['remove'].append(r)
        #from pudb import set_trace; set_trace()
        log = self.build_msg(results, html=html, std_out=std_out)
        self.log.append(log)
        #print('\n'.join(rr))

        #group = self.sort_group(group)
        #msg = {'keep': [], 'remove': [], 'tests_msg': ''}
        ##msg['keep'].extend(self.print_event(group[0]))
        #msg['keep'] = '\n'.join(self.print_event(group[0]))
        #tests_passed, tests_msg = self.run_group_tests(group)
        #msg['tests_msg'] = tests_msg
        #for i in group[1:]:
            #m = {'event'}
            #m['event'] = self.print_event(i)
            #msg['remove']['events'].append(self.print_event(i))
            #if not dry_run and tests_passed:
                #result = self.move_event(i_id, i_calendar_id,
                                         #destination_calendar_id)


        #keep = group[0]
        #move = group[1:]




        #print('Keep')
        #self.print_event(keep)
        ##try:
            ##keep_id = keep.get('id')
            ##keep_calendar_id = keep.get('organizer').get('email')
            ##msg['keep'].extend(self.print_event(keep_id, keep_calendar_id))
        ##except:
            ##return False
        ## move all the other events
        #tests_passed, msg = self.run_group_tests(group)
        #print msg
        #for i in move:
            #print '\n'
            #try:
                #i_id = i.get('id')
                #i_calendar_id = i.get('organizer').get('email')
                #self.print_event(i_id, i_calendar_id)
                #if not dry_run and tests_passed:
                    #self.move_event(i_id, i_calendar_id,
                                    #destination_calendar_id)
            #except:
                #continue

    def sort_group(self, group):
        """Sort the events in a group to determine which event to keep."""
        events = []
        #if len(group) > 1 and self.is_same_sized(group):
        if len(group) > 1:
            events = sorted(group, key=lambda item: item['created'])
            events = sorted(events, 
                            key=self.get_text_len)
            #events = events[1:]
        return events

    def get_text_len(self, event):
        """Calculate the number of characters of certain event attributes.

        This is only used for sorting groups to determine which event should
        be kept.  In some cases, the duplicate events are caused by faulty 
        sync software which, in addition to duplicating events, also adds
        some junk characters to the duplicates.  In those cases, we use 
        this method to find the event with the smaller number of characters
        and consider it to be the "original" event.  
        """
        text_len = 0
        summary = event.get('summary')
        if summary:
            text_len += len(summary)
        description = event.get('description')
        if description:
            text_len += len(description)
        location = event.get('location')
        if location:
            text_len += len(location)
        return text_len

    def is_same_sized(self, group, threshold=.85):
        """Test to compare the size (number of characters) of grouped events.

        If the sizes of events in a group vary by more than a given threshold,
        we assume the events are not actually duplicates.
        """
        group = [g.copy() for g in group]
        self.remove_group_attrs(group)
        sizes = sorted([len(str(i)) for i in group])
        if sizes[0] / float(sizes[-1]) >= threshold:
            return True
        else:
            return False

    def remove_group_attrs(self, group, attrs=REMOVE_ATTRS):
        """Removes certain attributes from a copied event group.

        These are attributes which can be expected to differ among a group 
        of duplicate events.  The event id, for instance, would never be 
        the same.  
        """
        for g in group:
            for a in attrs:
                if g.get(a):
                    g.pop(a)

    def has_all_attrs(self, group):
        """Test to compare the number of attributes of grouped events.

        The first event in a group (the event to be kept), must have at least
        as many attributes as all the other events in the group.  This test 
        simply ensures that the duplicate/to-be-removed events do not have more
        attributes than the kept event. There is a chance for false positive 
        in cases where the kept event has sufficient number, but different 
        attributes than the removed events.  
        """
        lens = [len(g) for g in group]
        keep_len = lens[0]
        if keep_len >= sorted(lens)[-1]:
            return True
        else:
            return False

    def run_group_tests(self, group):
        """Test the uniqueness of grouped events."""
        if not self.is_same_sized(group):
            msg = 'Group skipped (due to size differences):'
            return (False, msg)
        elif not self.has_all_attrs(group):
            msg = 'Group skipped (due to missing attributes):'
            return (False, msg)
        else:
            return (True, 'Group (processed):')

    def move_event(self, event, destination_calendar_id):
        """Move an event to the destination calendar."""
        try:
            event_id = event.get('id')
            calendar_id = event.get('organizer').get('email')
            moved = self.gcal_events.move(calendarId=calendar_id, 
                                        eventId=event_id,
                                        destination=destination_calendar_id).execute()
            return True
        except:
            return False

    def print_event(self, event, html=True):
        """Build a list of strings describing an event."""
        #event_id = event.get('id')
        #calendar_id = event.get('organizer').get('email')
        #event = self.get_event(event_id, source_calendar_id)
        lines = []
        lines.append(event.get('summary').encode('utf-8'))
        lines.append(u'{} - {}'.format(event.get('start').get('dateTime'),
                               event.get('end').get('dateTime')))
        for attr in ['description']:
            if event.get(attr): 
                lines.append(u''.join(event.get(attr)).encode('utf-8'))
        for attr in ['location', 'recurrence', 'created', 'updated']:
            if event.get(attr):
                lines.append(u'{}: {}'.format(attr, event.get(attr)).encode('utf-8'))
        if html:
            sep = '<br>\n'
        else:
            sep = '\n'
        return sep.join(lines)
        #return lines
        #print('\n'.join(lines))
        #print '-'*15
        #for k,v in event.items():
            #print u'{}:  {}'.format(k,v).encode('utf-8')
        #print '-'*15

    def build_msg(self, results, html=True, std_out=False):
        """Build text describing the events of a group."""
        lines = []
        failed_msg = 'Move FAILED: event could not be moved'
        if html:
            failed_msg = '{}<br>'.format(failed_msg)
        if html:
            lines.append('\n<hr>\n')
        else:
            lines.append('\n{}\n'.format('='*50))
        if html:
            lines.append('<ul><li>')
        lines.extend(['', results['tests'], ''])
        if html:
            lines.append('</li><ul><li>')
        lines.extend(['Keep:', ''])
        if html:
            lines.append('<ul><li>')
        lines.append(self.print_event(results['keep'], html=html))
        if html:
            lines.append('</li></ul></li><li>')
        lines.extend(['', 'Move:', ''])
        if html:
            lines.append('<ul>')
        for i in results['remove']:
            if html:
                lines.append('<li>')
            if i['moved_result'] is False:
                lines.append(failed_msg)
            lines.append(self.print_event(i['event'], html=html))
            if html:
                lines.append('</li>')
            lines.append('')
        if html:
            lines.append('</ul></li></ul></ul>')
        lines.append('')
        joined = '\n'.join(lines)
        if std_out:
            print(joined)
        return joined 



class CLI(object):
    """A class to interface with GCalMover() from the command-line."""

    def run(self):
        """Deduplify google calendar(s) from the command-line."""
        self.get_creds_native()
        self.gcm = GCalMover(self.credentials)
        #from pudb import set_trace; set_trace()
        self.calendars = self.gcm.get_calendars()
        self.calendar_names = [i.get('summary') for i in self.calendars]
        self.prompt_calendars()
        #from pudb import set_trace; set_trace()
        self.gcm.process_calendar_dups(self.source_calendars, 
                                       self.destination_calendar,
                                       replace_text=[(r'\\n',''), 
                                                     (r'\\',''), 
                                                     (r'\n','')],
                                       #dry_run=False,
                                       dry_run=True,
                                       html=False,
                                       std_out=True)

    def get_creds_native(self):
        """Get oauth2 credentials authorizing access to google calendar."""
        SCOPE = ('https://www.googleapis.com/auth/calendar ' 
                'https://www.googleapis.com/auth/userinfo.email ' 
                'https://www.googleapis.com/auth/userinfo.profile')
        redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        flow = client.flow_from_clientsecrets('client_secret.json',
                                            scope=SCOPE,
                                            redirect_uri=redirect_uri)
        try:
            storage = Storage('credentials.dat')
            credentials = storage.get()
        except:
            credentials = None
        if credentials is None or credentials.invalid:
            auth_uri = flow.step1_get_authorize_url()
            webbrowser.open(auth_uri)
            auth_code = raw_input('Enter the auth code: ')
            credentials = flow.step2_exchange(auth_code)
            if storage:
                storage.put(credentials)
        self.credentials = credentials
        return credentials 

    def prompt_calendars(self):
        """Prompt user to choose source/destination calendars."""
        src = cli_prompt(self.calendar_names, multiple=True, 
                         title='Select Source Calendars')
        self.source_calendars = [self.calendars[i] for i in src]
        self.source_calendar_ids = [i.get('id') for i in self.source_calendars]
        self.source_calendar_names = [i.get('summary') for i in 
                                      self.source_calendars]
        dest_choices = [i for i in self.calendars 
                        if i not in self.source_calendars]
        dest_names = [i.get('summary') for i in dest_choices]
        dest = cli_prompt(dest_names, multiple=False, 
                         title='Select Destination Calendar')
        self.destination_calendar = dest_choices[dest[0]]
        self.destination_calendar_id = self.destination_calendar.get('id')
        self.destination_calendar_name = self.destination_calendar.get('summary')

        print('\n')
        print('Source Calendar(s):\n{}'.format(
                            '\n'.join(self.source_calendar_names)))
        print('')
        print('Destination Calendar:\n{}'.format(self.destination_calendar_name))
        print('\n')

        cont = raw_input('Continue? [y/n]: ')
        if cont not in ['y', 'Y']:
            raise SystemExit

        #from pudb import set_trace; set_trace()


def cli_prompt(_list, multiple=False, title=None, question='Make a selection'):
    """Present a list of choices and read the user's answer."""
    print('')
    if title:
        print('{}\n'.format(title))
    for n,i in enumerate(_list):
        print('({}) {}'.format(n, i))
    print('')
    if multiple:
        question = '{} (space separated)'.format(question)
    question = '{}: '.format(question)
    choices = raw_input(question)
    #from pudb import set_trace; set_trace()
    choices = choices.split(' ')
    choices = [int(i) for i in choices]
    return choices

def main():
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()

