//
//  TaskCell.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 17/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>

@class Task;
@class CheckView;

@interface TaskCell : UITableViewCell
{
	NSInteger taskId;

	CheckView *leftImage;
	UILabel *titleLabel;
	UILabel *infosLabel;
	
	id target;
	SEL action;
	
	BOOL isTapping;
}

@property (nonatomic, readonly) NSInteger taskId;
@property (nonatomic, retain) IBOutlet CheckView *leftImage;
@property (nonatomic, retain) IBOutlet UILabel *titleLabel;
@property (nonatomic, retain) IBOutlet UILabel *infosLabel;

- (void)setTask:(Task *)task target:(id)target action:(SEL)action;

@end
