//
//  FullFromDesktopState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 25/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "TaskCoachAppDelegate.h"
#import "FullFromDesktopState.h"
#import "FullFromDesktopCategoryState.h"
#import "SyncViewController.h"
#import "Configuration.h"
#import "i18n.h"
#import "CDDomainObject.h"

@implementation FullFromDesktopState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[FullFromDesktopState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)activated
{
	myController.label.text = _("Synchronizing...");
	[myController.activity stopAnimating];
	myController.progress.hidden = NO;

	// Delete all local objects
	NSFetchRequest *request = [[NSFetchRequest alloc] init];
	[request setEntity:[NSEntityDescription entityForName:@"CDDomainObject" inManagedObjectContext:getManagedObjectContext()]];
	[request setPredicate:[NSPredicate predicateWithFormat:@"file == %@", [Configuration configuration].cdCurrentFile]];
	NSError *error;
	NSArray *results = [getManagedObjectContext() executeFetchRequest:request error:&error];
	[request release];

	if (results)
	{
		for (CDDomainObject *object in results)
			[getManagedObjectContext() deleteObject:object];

		[self startWithFormat:"iii" count:1];
	}
	else
	{
		NSLog(@"Could not fetch objects: %@", [error localizedDescription]);
		[self cancel];
	}
}

- (void)onNewObject:(NSArray *)value
{
	myController.categoryCount = [[value objectAtIndex:0] intValue];
	myController.taskCount = [[value objectAtIndex:1] intValue];
	myController.effortCount = [[value objectAtIndex:2] intValue];
}

- (void)onFinished
{
	myController.state = [FullFromDesktopCategoryState stateWithNetwork:myNetwork controller:myController];
}

@end
