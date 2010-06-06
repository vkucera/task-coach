//
//  SyncViewController.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 24/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <UIKit/UIKit.h>

#import "Network.h"
#import "State.h"

@interface SyncViewController : UIViewController <NetworkDelegate>
{
	UILabel *label;
	UIActivityIndicatorView *activity;
	UIProgressView *progress;

	NSString *host;
	NSInteger port;

	NSObject <State> *state;
	Network *myNetwork;

	id target;
	SEL action;
	
	NSInteger protocolVersion;

	NSInteger categoryCount;
	NSInteger taskCount;
	NSInteger effortCount;
	NSInteger currentCount;
}

@property (nonatomic, retain) IBOutlet UILabel *label;
@property (nonatomic, retain) IBOutlet UIActivityIndicatorView *activity;
@property (nonatomic, retain) IBOutlet UIProgressView *progress;

@property (nonatomic, retain) NSObject <State> *state;
@property (nonatomic) NSInteger protocolVersion;

@property (nonatomic) NSInteger categoryCount;
@property (nonatomic) NSInteger taskCount;
@property (nonatomic) NSInteger effortCount;

- initWithTarget:(id)target action:(SEL)action host:(NSString *)host port:(NSInteger)port;

- (void)finished:(BOOL)ok;

- (void)cancel;
- (void)increment;

@end
