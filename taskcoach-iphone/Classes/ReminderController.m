//
//  ReminderController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 06/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "TaskCoachAppDelegate.h"
#import "ReminderController.h"
#import "CDDomainObject+Addons.h"
#import "CDTask.h"
#import "CDTask+Addons.h"
#import "LogUtils.h"
#import "i18n.h"

#import <AudioToolbox/AudioToolbox.h>

static ReminderController *_instance = NULL;

@interface ReminderDelegate : NSObject
{
	CDTask *task;
}

- initWithTask:(CDTask *)theTask;

@end

@implementation ReminderDelegate

- initWithTask:(CDTask *)theTask
{
	if ((self = [super init]))
	{
		task = [theTask retain];
	}
	
	return self;
}

- (void)dealloc
{
	[task release];
	[super dealloc];
}

- (void)alertView:(UIAlertView *)alertView didDismissWithButtonIndex:(NSInteger)buttonIndex
{
	if (buttonIndex == 1)
	{
		task.completionDate = [NSDate date];
		[task computeDateStatus];
		[task markDirty];
		
		NSError *error;
		if (![getManagedObjectContext() save:&error])
		{
			JLERROR("Could not save: %s", [[error localizedDescription] UTF8String]);
		}
	}

	[self release];
}

@end

@implementation ReminderController

+ (ReminderController *)instance
{
	if (!_instance)
		_instance = [[ReminderController alloc] init];
	return _instance;
}

- (void)check:(BOOL)silent
{
	NSFetchRequest *request = [[NSFetchRequest alloc] init];
	[request setEntity:[NSEntityDescription entityForName:@"CDTask" inManagedObjectContext:getManagedObjectContext()]];
	[request setPredicate:[NSPredicate predicateWithFormat:@"reminderDate != NULL AND reminderDate <= %@", [NSDate date]]];
	NSError *error;
	NSArray *results = [getManagedObjectContext() executeFetchRequest:request error:&error];
	[request release];

	if (results)
	{
		for (CDTask *task in results)
		{
			if (silent)
			{
				task.completionDate = [NSDate date];
				[task computeDateStatus];
				[task markDirty];
				
				NSError *error;
				if (![getManagedObjectContext() save:&error])
				{
					JLERROR("Could not save: %s", [[error localizedDescription] UTF8String]);
				}
			}
			else
			{
				ReminderDelegate *delegate = [[ReminderDelegate alloc] initWithTask:task];
				UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Reminder") message:task.name delegate:delegate cancelButtonTitle:_("OK") otherButtonTitles:nil];
				[alert addButtonWithTitle:_("Completed")];
				[alert show];
				[alert release];
			}
			
			task.reminderDate = nil;
			[task markDirty];
		}
		
		if (![getManagedObjectContext() save:&error])
		{
			JLERROR("Could not save (reminders): %s", [[error localizedDescription] UTF8String]);
		}
	}
}

- (void)scheduleLocalNotifications
{
	NSFetchRequest *request = [[NSFetchRequest alloc] init];
	[request setEntity:[NSEntityDescription entityForName:@"CDTask" inManagedObjectContext:getManagedObjectContext()]];
	[request setPredicate:[NSPredicate predicateWithFormat:@"reminderDate != NULL"]];
	
	NSError *error;
	NSArray *results = [getManagedObjectContext() executeFetchRequest:request error:&error];
	[request release];

	if (results)
	{
		for (CDTask *task in results)
		{
			UILocalNotification *notif = [[UILocalNotification alloc] init];
			if (!notif)
				return;
			
			notif.fireDate = task.reminderDate;
			notif.timeZone = [NSTimeZone defaultTimeZone];
			notif.alertBody = task.name;
			notif.alertAction = _("Completed");
			notif.soundName = UILocalNotificationDefaultSoundName;
			notif.applicationIconBadgeNumber = 0;
			notif.userInfo = [NSDictionary dictionaryWithObjectsAndKeys:[[[task objectID] URIRepresentation] absoluteString], @"CoreID", nil];
			[[UIApplication sharedApplication] scheduleLocalNotification:notif];
			[notif release];
		}
	}
}

- (void)unscheduleLocalNotifications
{
	[[UIApplication sharedApplication] cancelAllLocalNotifications];
}

@end
