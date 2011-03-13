//
//  CDDomainObject+Addons.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 30/05/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "Task_CoachAppDelegate.h"
#import "CDDomainObject+Addons.h"
#import "i18n.h"

@implementation CDDomainObject (Addons)

- (BOOL)save
{
	NSError *error;
	if (![getManagedObjectContext() save:&error])
	{
		UIAlertView *alert = [[UIAlertView alloc] initWithTitle:@"Error" message:[NSString stringWithFormat:@"Could not save %@: %@", [[self entity] name], [error localizedDescription]] delegate:self cancelButtonTitle:@"OK" otherButtonTitles:nil];
		[alert show];
		[alert release];

		return NO;
	}

	return YES;
}

- (void)updateStatus:(NSInteger)newStatus
{
	switch ([self.status intValue])
	{
		case STATUS_NEW:
		case STATUS_MODIFIED:
			if (newStatus != STATUS_DELETED)
				newStatus = [self.status intValue];
			break;
		case STATUS_DELETED:
			newStatus = STATUS_DELETED;
			break;
	}

	self.status = [NSNumber numberWithInt:newStatus];
}

- (void)markDirty
{
	[self updateStatus:STATUS_MODIFIED];
}

- (void)delete
{
	if ([self.status intValue] == STATUS_NEW)
	{
		[getManagedObjectContext() deleteObject:self];
	}
	else
	{
		[self updateStatus:STATUS_DELETED];
	}
}

@end
