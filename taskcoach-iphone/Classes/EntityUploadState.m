//
//  EntityUploadState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 05/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "TaskCoachAppDelegate.h"
#import "EntityUploadState.h"
#import "CDDomainObject.h"
#import "CDDomainObject+Addons.h"
#import "SyncViewController.h"
#import "Configuration.h"

@implementation EntityUploadState

- (void)dealloc
{
	[objects release];

	[super dealloc];
}

- (void)activated
{
	NSFetchRequest *request = [[NSFetchRequest alloc] init];
	[request setEntity:[NSEntityDescription entityForName:[self entityName] inManagedObjectContext:getManagedObjectContext()]];
	[request setPredicate:[NSPredicate predicateWithFormat:@"file == %@ AND status == %d", [Configuration configuration].cdCurrentFile, [self status]]];
	
	if ([self ordering])
	{
		NSSortDescriptor *sd = [[NSSortDescriptor alloc] initWithKey:[self ordering] ascending:YES];
		[request setSortDescriptors:[NSArray arrayWithObject:sd]];
		[sd release];
	}
	
	NSError *error;
	objects = [[getManagedObjectContext() executeFetchRequest:request error:&error] retain];
	[request release];

	if (objects)
	{
		if ([objects count] == 0)
		{
			[self onFinished];
		}
		else
		{
			[self packObject:[objects objectAtIndex:index]];
			[self startWithFormat:"s" count:[objects count]];
		}
	}
	else
	{
		NSLog(@"Could not fetch %@: %@", [self entityName], [error localizedDescription]);
		[self cancel];
	}
}

- (void)onNewObject:(NSArray *)value
{
	if ([self status] == STATUS_NEW)
	{
		CDDomainObject *object = [objects objectAtIndex:index];
		object.taskCoachId = [value objectAtIndex:0];

		NSLog(@"Got ID: %@", object.taskCoachId);
	}

	++index;
	
	if (index < [objects count])
	{
		[self packObject:[objects objectAtIndex:index]];
	}
}

#pragma mark Virtual

- (void)packObject:(NSManagedObject *)object
{
}

- (NSString *)entityName
{
	return nil;
}

- (NSInteger)status
{
	return -1;
}

- (NSString *)ordering
{
	return nil;
}

@end
