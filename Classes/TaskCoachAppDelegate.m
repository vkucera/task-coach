//
//  TaskCoachAppDelegate.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright Jérôme Laheurte 2009. See COPYING for details.
//

#import "TaskCoachAppDelegate.h"
#import "PositionStore.h"
#import "i18n.h"

@implementation TaskCoachAppDelegate

@synthesize window;
@synthesize mainController;

- (void)applicationDidFinishLaunching:(UIApplication *)application
{
	// These lines are just there so that gettext can retrieve strings
	// in the NIB. Remember to add a line here each time a translatable
	// string appears in a NIB.

	_("Cancel");
	_("Save");
	_("Categories");
	_("Sync");

	[window addSubview:mainController.view];
	
	[window makeKeyAndVisible];
}

- (void)dealloc
{
	[mainController release];
    [window release];

    [super dealloc];
}

- (void)applicationWillTerminate:(UIApplication *)application
{
	UIViewController *ctrl = [mainController topViewController];
	
	if ([ctrl respondsToSelector:@selector(willTerminate)])
		[ctrl performSelector:@selector(willTerminate)];
	
	
	NSArray *cachesPaths = NSSearchPathForDirectoriesInDomains(NSCachesDirectory, NSUserDomainMask, YES);
	NSString *cachesDir = [cachesPaths objectAtIndex:0];
	
	NSFileManager *fileManager = [NSFileManager defaultManager];
	if (![fileManager fileExistsAtPath:cachesDir])
	{
		[fileManager createDirectoryAtPath:cachesDir attributes:nil];
	}
	
	NSString *path = [cachesDir stringByAppendingPathComponent:@"positions.store"];
	[[PositionStore instance] save:path];

	[fileManager release];
}

@end
