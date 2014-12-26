#!/usr/bin/env python2

from lxml import etree
import sys
import re
import httplib2
from apiclient.discovery import build


REMOVE_ATTRS = ['id', 'htmlLink', 'iCalUID', 'gadget', 'attendees']

def output_rpt_line():
    print '\n\n{0}\n{0}\n\n'.format('='*78)

class GCalMover(object):
    def __init__(self, credentials):
        self.credentials = credentials
        self.get_gcal_service()

    def get_gcal_service(self):
        # Create an httplib2.Http object to handle our HTTP requests, 
        # and authorize it using the credentials.authorize() function.
        http = httplib2.Http()
        http = self.credentials.authorize(http)
        # The apiclient.discovery.build() function returns an instance of an 
        # API service
        # object can be used to make API calls. The object is constructed with
        # methods specific to the calendar API. The arguments provided are:
        #   name of the API ('calendar')
        #   version of the API you are using ('v3')
        #   authorized httplib2.Http() object that can be used for API calls
        self.service = build('calendar', 'v3', http=http)

    def get_calendars(self):
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
                              destination_calendar_id=None,
                              replace_text=[],
                              dry_run=False):
        # replace_text example (VEA): [(r'\\n',''), (r'\\',''), (r'\n','')]
        self.destination_calendar_id = destination_calendar_id
        self.replace_text = replace_text
        self.find_dup_groups()
        self.process_groups(dry_run=dry_run)

    def find_dup_groups(self):
        self.events = {}
        page_token = None
        while True:
            page = self.gcal_events.list(calendarId=self.source_calendar_id,
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

                    # build a tuple from 5 attributes with which we test uniqueness
                    item_key = (start, end, recurrence, summary, description, location)
                    
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


    def process_groups(self, dry_run=False):
        for k,v in self.events.items():
            if len(v) > 1:
                group = self.sort_group(v)
                ids = [i['id'] for i in group]
                # print info on the selected "original" event:
                output_rpt_line()
                print 'KEEP:'
                self.print_event(ids[0], self.source_calendar_id)
                # move all the other events
                tests_passed, msg = self.run_group_tests(group)
                print msg
                for i in ids[1:]:
                    print '\n'
                    self.print_event(i, self.source_calendar_id)
                    if not dry_run and tests_passed:
                        self.move_event(i, self.source_calendar_id,
                                        self.destination_calendar_id)

    def sort_group(self, group):
        events = []
        #if len(group) > 1 and self.is_same_sized(group):
        if len(group) > 1:
            events = sorted(group, key=lambda item: item['created'])
            events = sorted(events, 
                            key=self.get_text_len)
            #events = events[1:]
        return events

    def get_text_len(self, event):
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
        group = [g.copy() for g in group]
        self.remove_group_attrs(group)
        sizes = sorted([len(str(i)) for i in group])
        if sizes[0] / float(sizes[-1]) >= threshold:
            return True
        else:
            return False

    def remove_group_attrs(self, group, attrs=REMOVE_ATTRS):
        for g in group:
            for a in attrs:
                if g.get(a):
                    g.pop(a)

    def has_all_attrs(self, group):
        lens = [len(g) for g in group]
        keep_len = lens[0]
        if keep_len >= sorted(lens)[-1]:
            return True
        else:
            return False

    def run_group_tests(self, group):
        if not self.is_same_sized(group):
            msg = '\n\nNOT MOVED (due to size differences):'
            return (False, msg)
        elif not self.has_all_attrs(group):
            msg = '\n\nNOT MOVED (due to missing attributes):'
            return (False, msg)
        else:
            return (True, '\n\nMOVE:')

    def move_event(self, event_id, source_calendar_id, destination_calendar_id):
        try:
            moved = self.gcal_events.move(calendarId=source_calendar_id, 
                                        eventId=event_id,
                                        destination=destination_calendar_id).execute()
        except:
            moved = None
            print 'MOVE_ERROR: event could not be moved (event id: {})'.format(event_id)
        return moved

    def get_event(self, event_id, source_calendar_id):
        event = self.gcal_events.get(calendarId=source_calendar_id, 
                                      eventId=event_id).execute()
        return event

    def print_event(self, event_id, source_calendar_id):
        event = self.get_event(event_id, source_calendar_id)
        print event.get('summary').encode('utf-8')
        print u'{} - {}'.format(event.get('start').get('dateTime'),
                               event.get('end').get('dateTime'))
        for attr in ['recurrence', 'description', 'location']:
            if event.get(attr): print u''.join(event.get(attr)).encode('utf-8')
        print '-'*15
        for k,v in event.items():
            print u'{}:  {}'.format(k,v).encode('utf-8')
        print '-'*15

def main():
    src_cal = 'sample_calendar_id'
    dest_cal = 'sample_calendar_id'
    gcm = GCalMover(calendar_id=src_cal)
    gcm.process_calendar_dups(destination_calendar_id=dest_cal,
                              #dry_run=True,
                              #include_desc=True,
                              replace_text=[(r'\\n',''), (r'\\',''), (r'\n','')])

if __name__ == '__main__':
  main()
